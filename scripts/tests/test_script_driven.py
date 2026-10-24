"""Project choices, deterministic media timing and Remotion-only composition."""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from validate_storyboard import validate
from query_knowledge import search, sources, capabilities, read
from build_ai_video_audio_stem import clip_timing, tempo_filter
ROOT = Path(__file__).resolve().parents[2]

class AudioTimingTests(unittest.TestCase):
    def test_speed_changes_match_video_window(self):
        self.assertEqual(clip_timing({'duration':3, 'playback_rate':.5}, 6)['playback_rate'], .5)
        with self.assertRaises(ValueError):
            clip_timing({'duration':3, 'playback_rate':.5}, 5)
    def test_chained_tempo_preserves_total_factor(self):
        for rate in (.125, .5, 1, 1.25, 4, 8):
            factors = [float(x.split('=')[1]) for x in tempo_filter(rate).split(',')]
            product = 1
            for factor in factors:
                self.assertTrue(.5 <= factor <= 2)
                product *= factor
            self.assertAlmostEqual(product, rate)
    def test_bad_timing_is_not_silently_clamped(self):
        for key, value in [('source_start',-1), ('playback_rate',0), ('duration',float('inf')),
                           ('timeline_start',True), ('duration',-1)]:
            with self.assertRaises(ValueError):
                clip_timing({'duration':1, key:value}, 6)

class ScriptDrivenTests(unittest.TestCase):
    def setUp(self):
        self.data = read('assets/templates/storyboard-example.json')
    def assert_valid(self):
        self.assertTrue(validate(self.data)['ok'], validate(self.data))
    def assert_invalid(self):
        self.assertFalse(validate(self.data)['ok'])
    def test_new_example(self):
        self.assert_valid()
    def test_static_original_scene_without_source_paperwork(self):
        self.data.pop('reference_sources')
        for scene in self.data['scenes']:
            scene.pop('reference_uses')
            scene.pop('motion_beats')
            scene['start_state'] = scene['end_state'] = '真实史料静态展示，便于阅读'
        self.assert_valid()
    def test_only_remotion_can_compose_the_master(self):
        for schema in (6, 7):
            self.setUp()
            self.data['schema_version'] = schema
            self.data['engine'] = 'html-playwright'
            self.assert_invalid()
            self.data['engine'] = 'remotion'
            self.data['scenes'][1]['engine'] = 'canvas-prerender'
            self.assert_invalid()
    def test_missing_engine_still_fails(self):
        del self.data['engine']
        self.assert_invalid()
    def test_no_presenter_or_ai_media_requires_no_confirmation(self):
        self.assertNotIn('ai_video', self.data['production_policy'])
        self.assert_valid()
        self.assertFalse(any('confirmation' in w for w in validate(self.data)['warnings']))
    def test_fixed_presenter_treatment_is_preserved(self):
        self.data['production_policy']['presenter'] = {'opening_fullscreen_seconds':2,'later_mode':'left_pip'}
        self.assert_invalid()
    def test_short_full_film_is_supported(self):
        self.data['scope'] = 'full_film'
        self.assert_valid()
    def test_fixed_opening_applies_to_available_film_range(self):
        self.data['production_policy']['presenter']['opening_fullscreen_seconds'] = 15
        self.assert_valid()
        self.data['scope'] = 'full_film'
        self.data['duration_frames'] = 1200
        self.data['scenes'][-1]['end_frame_exclusive'] = 1200
        self.assert_valid()
    def test_old_schema_decisions_are_read_without_silent_rewriting(self):
        self.data['schema_version'] = 6
        self.data['scope'] = 'excerpt'
        self.data['production_policy']['presenter'] = {'opening_fullscreen_seconds':15,'later_mode':'bottom_right_pip'}
        self.data['production_policy']['ai_video'] = {'duration_confirmation':'pending','durations_seconds':{}}
        before = copy.deepcopy(self.data)
        self.assert_valid()
        self.assertEqual(self.data, before)
    def test_subtitles_can_be_chosen_without_user_override_text(self):
        self.data['production_policy']['subtitles']['mode'] = 'burned'
        for scene in self.data['scenes']:
            scene['texts'][0]['role'] = 'subtitle_zh'
        self.assert_valid()
        self.data['production_policy']['subtitles']['mode'] = 'external'
        self.assert_invalid()
    def test_shared_style_does_not_allow_unrelated_skin(self):
        self.data['scenes'][1]['style_system_id'] = 'unrelated-template'
        self.assert_invalid()
    def test_style_contract_required(self):
        del self.data['style_system']
        self.assert_invalid()
    def test_actual_source_mapping_still_required(self):
        self.data['scenes'][0]['source_ids'] = ['invented']
        self.assert_invalid()
    def test_invalid_reference_not_ignored(self):
        self.data['scenes'][0]['reference_uses'][0]['source_id'] = 'unknown'
        self.assert_invalid()
    def add_media(self):
        self.data['production_policy']['ai_video'] = {'duration_confirmation':'confirmed',
            'durations_seconds':{'clip':3}, 'confirmation_basis':'本次用户确认的时长表：clip为3秒'}
        for i, scene in enumerate(self.data['scenes']):
            scene['media_layers'] = [{'asset_id':'clip', 'playback_id':f'play-{i}', 'kind':'ai_video',
                'availability':'pending', 'path':None, 'source_in_seconds':2+i,
                'source_out_seconds':5+i, 'playback_rate':1,
                'visible_start_frame':scene['start_frame'],
                'visible_end_frame_exclusive':scene['end_frame_exclusive']}]
    def test_per_asset_windows_and_reuse_allowed(self):
        self.add_media()
        self.assert_valid()
        layer = self.data['scenes'][1]['media_layers'][0]
        layer.update(source_in_seconds=4, source_out_seconds=5.5, playback_rate=0.5)
        self.assert_valid()
    def test_ai_duration_must_match_current_user_input(self):
        self.add_media()
        self.data['production_policy']['ai_video']['durations_seconds']['clip'] = 10
        self.assert_invalid()
    def test_only_explicitly_required_confirmation_blocks_production(self):
        self.add_media()
        self.data['production_policy']['ai_video'] = {'duration_confirmation_required':True,
                                                     'duration_confirmation':'pending','durations_seconds':{}}
        self.assert_valid()
        self.assertTrue(any('awaiting' in w for w in validate(self.data)['warnings']))
        self.data['scenes'][0]['verification'] = 'implemented'
        self.assert_invalid()
    def test_project_can_select_media_timing_without_new_approval(self):
        self.add_media()
        self.data['production_policy'].pop('ai_video')
        self.data['scenes'][0]['verification'] = 'implemented'
        self.assert_valid()
    def test_confirmation_requires_each_asset_duration_and_basis(self):
        self.add_media()
        self.data['production_policy']['ai_video']['durations_seconds'] = {}
        self.assert_invalid()
        self.add_media()
        del self.data['production_policy']['ai_video']['confirmation_basis']
        self.assert_invalid()
    def test_wrong_source_clock_rejected(self):
        self.add_media()
        self.data['scenes'][1]['media_layers'][0]['source_out_seconds'] = 99
        self.assert_invalid()
    def test_cross_scene_playback_cannot_change_source(self):
        self.add_media()
        for scene in self.data['scenes']:
            layer = scene['media_layers'][0]
            layer.update(playback_id='shared', source_in_seconds=0, source_out_seconds=6,
                         visible_start_frame=0, visible_end_frame_exclusive=360)
        self.data['production_policy']['ai_video']['durations_seconds']['clip'] = 6
        self.assert_valid()
        self.data['scenes'][1]['media_layers'][0].update(source_in_seconds=1, source_out_seconds=7)
        self.assert_invalid()
    def test_invalid_rate_and_source_values(self):
        for key, value in [('playback_rate',0), ('playback_rate',float('nan')),
                           ('source_in_seconds',-1), ('source_out_seconds',True)]:
            self.setUp()
            self.add_media()
            self.data['scenes'][0]['media_layers'][0][key] = value
            self.assert_invalid()
    def test_pending_media_is_plan_not_render_ready(self):
        self.add_media()
        with tempfile.TemporaryDirectory() as folder:
            self.assertFalse(validate(self.data, Path(folder))['ok'])
    def test_unsupported_subtitle_mode_and_safe_area_fail(self):
        self.data['production_policy']['subtitles']['mode'] = 'automatic-magic'
        self.assert_invalid()
        self.setUp()
        self.data['production_policy']['subtitles']['reserve_space'] = True
        self.assert_invalid()
    def test_fake_rendered_status_still_fails(self):
        self.data['scenes'][0]['verification'] = 'rendered'
        self.assert_invalid()

class KnowledgeTests(unittest.TestCase):
    def test_offline_chinese_sentence_retrieves_relevant_card(self):
        result = search('这一段需要对比税收数据和表格', limit=1)
        self.assertEqual(result['results'][0]['id'], 'quantitative-comparison')
        self.assertTrue(result['materials'])
        self.assertTrue(result['sources'])
    def test_lookup_static_evidence_without_cache(self):
        self.assertEqual(search('史料细节放大证据', limit=1)['results'][0]['id'], 'evidence-focus')
    def test_material_recipes_distinguish_implementation(self):
        hit = search('数据表格', materials=True, limit=1)['results'][0]
        self.assertEqual(hit['id'], 'comparison-stage')
        self.assertIn('implementation_required', hit['status'])
    def test_no_match_does_not_fabricate_reference(self):
        self.assertEqual(search('xyz-no-such-cue-83727')['results'], [])
    def test_all_knowledge_links_resolve(self):
        inventory = sources()
        cards = read('references/knowledge-cards.json')['cards']
        materials = read('assets/material-library.json')['materials']
        ids = {c['id'] for c in cards}
        mids = {m['id'] for m in materials}
        self.assertEqual(len(ids), len(cards))
        self.assertEqual(len(mids), len(materials))
        self.assertEqual({c['id'] for c in capabilities()}, ids)
        for card in cards:
            self.assertTrue(set(card['sources']).issubset(inventory), card['id'])
            self.assertTrue(set(card['materials']).issubset(mids))
        for material in materials:
            self.assertTrue(set(material['cards']).issubset(ids))
            for component in material['components']:
                path, symbol = component.split('#')
                self.assertIn('export const '+symbol, (ROOT/path).read_text(encoding='utf-8'))
    def test_excluded_source_stays_excluded(self):
        self.assertEqual(search('',source_id='draw-with-code')['status'], 'unresolved')
        self.assertEqual(search('',source_id='gc-minimal-zine-poster')['status'], 'excluded_by_user')
    def test_tangential_and_incompatible_are_not_called_implemented(self):
        self.assertEqual(search('',source_id='wise-motion')['source']['integration'], 'local_production_module')
        self.assertIn('Noncommercial', search('',source_id='video-talkcraft')['source']['license'])
    def test_unknown_card_fails(self):
        with self.assertRaises(ValueError):
            search('',card_id='nonexistent')
    def test_cli_knowledge_runs_without_cache(self):
        with tempfile.TemporaryDirectory() as folder:
            run = subprocess.run([sys.executable,'-X','utf8',str(ROOT/'scripts/query_motion_library.py'),
                    '--knowledge','--card','editorial-collage','--cache-root',folder],
                    text=True,encoding='utf-8',capture_output=True)
            self.assertEqual(run.returncode,0,run.stderr)
            self.assertEqual(json.loads(run.stdout)['results'][0]['id'],'editorial-collage')
    def test_versions_and_scope_are_preserved(self):
        for source in read('references/research-sources.json')['sources']:
            self.assertRegex(source['audited_commit'], r'^[a-f0-9]{40}$')
            self.assertTrue(source['reviewed_documents'])
            self.assertIsInstance(source['copied_code'], bool)
            self.assertTrue((ROOT / source['local_path'] / 'source.json').is_file())

if __name__ == '__main__':
    unittest.main()
