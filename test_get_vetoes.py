# FILE: test_get_vetoes.py
import os
import unittest
from unittest.mock import patch, mock_open, MagicMock
import json
import get_vetoes

class TestGetVetoes(unittest.TestCase):

    def setUp(self):
        # Construct the absolute path to the examples directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        examples_dir = os.path.join(current_dir, 'examples')
        bo3_example_file_path = os.path.join(examples_dir, 'example_bo3_match.json')
        # Load example_bo3_match.json content from the examples directory
        with open(bo3_example_file_path, 'r') as file:
            self.example_bo3_match = json.load(file)

        # Sample match data structure
        self.match_data = {
            'voting': {
                'map': {
                    'pick': ['de_dust2', 'de_inferno', 'de_mirage']
                }
            },
            "detailed_results": [
                {
                    "asc_score": False,
                    "winner": "faction1",
                    "factions": {
                        "faction1": {
                            "score": 1
                        },
                        "faction2": {
                            "score": 0
                        }
                    }
                },
                {
                    "asc_score": False,
                    "winner": "faction2",
                    "factions": {
                        "faction2": {
                            "score": 1
                        },
                        "faction1": {
                            "score": 0
                        }
                    }
                },
                {
                    "asc_score": False,
                    "winner": "faction1",
                    "factions": {
                        "faction2": {
                            "score": 0
                        },
                        "faction1": {
                            "score": 1
                        }
                    }
                }
    ]
        }

    @patch('builtins.open', new_callable=mock_open, read_data='{"key": "value"}')
    def test_get_config_data_from_file(self, mock_file):
        result = get_vetoes.get_config_data_from_file('config.json')
        self.assertEqual(result, {"key": "value"})
        mock_file.assert_called_once_with('config.json', 'r')

    def test_retrieve_faceit_api_get_match_url(self):
        match_id = "12345"
        expected_url = f"https://open.faceit.com/data/v4/matches/{match_id}"
        result = get_vetoes.retrieve_faceit_api_get_match_url(match_id)
        self.assertEqual(result, expected_url)

    def test_retrieve_faceit_api_veto_url(self):
        match_id = "12345"
        expected_url = f"https://api.faceit.com/democracy/v1/match/{match_id}/history"
        result = get_vetoes.retrieve_faceit_api_veto_url(match_id)
        self.assertEqual(result, expected_url)

    def test_get_map_object(self):
        expected_map_object = {
            'played': 0,
            'picked': 0,
            'banned': 0,
            'random_ban': 0,
            'wins': 0,
            'unfinished': 0,
            'not_played': 0
        }
        result = get_vetoes.get_map_object()
        self.assertEqual(result, expected_map_object)

    # @patch('get_vetoes.requests.get')
    # def test_get_match_vetoes_success(self, mock_get):
    #     mock_response = MagicMock()
    #     mock_response.status_code = 200
    #     mock_response.json.return_value = {"key": "value"}
    #     mock_get.return_value = mock_response

    #     result = get_vetoes.get_match_vetoes("12345")
    #     self.assertEqual(result, {"key": "value"})
    #     mock_get.assert_called_once_with("https://api.faceit.com/democracy/v1/match/12345/history")

    # @patch('get_vetoes.requests.get')
    # def test_get_match_vetoes_failure(self, mock_get):
    #     mock_response = MagicMock()
    #     mock_response.status_code = 404
    #     mock_get.return_value = mock_response

    #     result = get_vetoes.get_match_vetoes("12345")
    #     self.assertIsNone(result)
    #     mock_get.assert_called_once_with("https://api.faceit.com/democracy/v1/match/12345/history")

    # @patch('get_vetoes.requests.get')
    # def test_get_match_success(self, mock_get):
    #     mock_response = MagicMock()
    #     mock_response.status_code = 200
    #     mock_response.json.return_value = {"key": "value"}
    #     mock_get.return_value = mock_response

    #     with patch.dict('os.environ', {'FACEIT_API_KEY': 'test_key'}):
    #         result = get_vetoes.get_match("12345")
    #         self.assertEqual(result, {"key": "value"})
    #         mock_get.assert_called_once_with(
    #             "https://open.faceit.com/data/v4/matches/12345",
    #             headers={'Authorization': 'Bearer test_key'}
    #         )

    # @patch('get_vetoes.requests.get')
    # def test_get_match_failure(self, mock_get):
    #     mock_response = MagicMock()
    #     mock_response.status_code = 404
    #     mock_get.return_value = mock_response

    #     with patch.dict('os.environ', {'FACEIT_API_KEY': 'test_key'}):
    #         result = get_vetoes.get_match("12345")
    #         self.assertIsNone(result)
    #         mock_get.assert_called_once_with(
    #             "https://open.faceit.com/data/v4/matches/12345",
    #             headers={'Authorization': 'Bearer test_key'}
    #         )

    def test_update_map_play_data_with_initial_values(self):
        get_vetoes.team_data = {'maps': {}}
        get_vetoes.update_map_play_data('map1', picked=1, wins=1)
        expected_data = {
            'map1': {
                'played': 0,
                'picked': 1,
                'banned': 0,
                'random_ban': 0,
                'wins': 1,
                'unfinished': 0,
                'not_played': 0
            }
        }
        self.assertEqual(get_vetoes.team_data['maps'], expected_data)

    def test_update_map_play_data_with_existing_map(self):
        get_vetoes.team_data = {
            'maps': {
                'map1': {
                    'played': 1,
                    'picked': 1,
                    'banned': 0,
                    'random_ban': 0,
                    'wins': 1,
                    'unfinished': 0,
                    'not_played': 0
                }
            }
        }
        get_vetoes.update_map_play_data('map1', picked=1, wins=1)
        expected_data = {
            'map1': {
                'played': 1,
                'picked': 2,
                'banned': 0,
                'random_ban': 0,
                'wins': 2,
                'unfinished': 0,
                'not_played': 0
            }
        }
        self.assertEqual(get_vetoes.team_data['maps'], expected_data)

    def test_update_map_play_data_with_multiple_maps(self):
        get_vetoes.team_data = {'maps': {}}
        get_vetoes.update_map_play_data('map1', picked=1, wins=1)
        get_vetoes.update_map_play_data('map2', picked=2, wins=1)
        expected_data = {
            'map1': {
                'played': 0,
                'picked': 1,
                'banned': 0,
                'random_ban': 0,
                'wins': 1,
                'unfinished': 0,
                'not_played': 0
            },
            'map2': {
                'played': 0,
                'picked': 2,
                'banned': 0,
                'random_ban': 0,
                'wins': 1,
                'unfinished': 0,
                'not_played': 0
            }
        }
        self.assertEqual(get_vetoes.team_data['maps'], expected_data)

    def test_update_map_play_data_with_no_initial_data(self):
        get_vetoes.team_data = {'maps': {}}
        get_vetoes.update_map_play_data('map1')
        expected_data = {
            'map1': {
                'played': 0,
                'picked': 0,
                'banned': 0,
                'random_ban': 0,
                'wins': 0,
                'unfinished': 0,
                'not_played': 0
            }
        }
        self.assertEqual(get_vetoes.team_data['maps'], expected_data)

    def test_update_map_play_data_with_all_parameters(self):
        # Initialize team_data with an existing map
        get_vetoes.team_data = {'maps': {'map1': {
            'played': 2,
            'picked': 1,
            'banned': 1,
            'random_ban': 0,
            'wins': 1,
            'unfinished': 0,
            'not_played': 0
        }}}

        # Call the function with all parameters
        get_vetoes.update_map_play_data(
            'map1',
            played=1,
            picked=1,
            banned=1,
            random_ban=1,
            wins=1,
            unfinished=1,
            not_played=1
        )

        # Expected data after the update
        expected_data = {
            'map1': {
                'played': 3,       # 2 + 1
                'picked': 2,       # 1 + 1
                'banned': 2,       # 1 + 1
                'random_ban': 1,   # 0 + 1
                'wins': 2,         # 1 + 1
                'unfinished': 1,   # 0 + 1
                'not_played': 1    # 0 + 1
            }
        }

        # Assert that the team_data was updated correctly
        self.assertEqual(get_vetoes.team_data['maps'], expected_data)

    def test_map_played(self):
        # Test when the map was played
        self.assertTrue(get_vetoes.was_map_played(self.example_bo3_match, 'de_ancient'))
        self.assertTrue(get_vetoes.was_map_played(self.example_bo3_match, 'de_vertigo'))
        self.assertTrue(get_vetoes.was_map_played(self.example_bo3_match, 'de_overpass'))

    def test_map_not_played(self):
        # Test when the map was not played
        self.assertFalse(get_vetoes.was_map_played(self.example_bo3_match, 'de_mirage'))
        self.assertFalse(get_vetoes.was_map_played(self.example_bo3_match, 'de_anubis'))
        self.assertFalse(get_vetoes.was_map_played(self.example_bo3_match, 'de_dust2'))
        self.assertFalse(get_vetoes.was_map_played(self.example_bo3_match, 'de_inferno'))

    def test_map_not_played_empty_detailed_results(self):
        # Test when detailed_results is empty
        match_data_empty_results = {
            'voting': {
                'map': {
                    'pick': ['de_dust2', 'de_inferno', 'de_mirage']
                }
            },
            'detailed_results': []
        }
        self.assertFalse(get_vetoes.was_map_played(match_data_empty_results, 'de_dust2'))

    # def test_is_match_finished(self):
    #     match = {'status': 'FINISHED'}
    #     self.assertTrue(get_vetoes.is_match_finished(match))

    #     match = {'status': 'ONGOING'}
    #     self.assertFalse(get_vetoes.is_match_finished(match))

    # def test_determine_faction(self):
    #     get_vetoes.faceit_team_id = "team1"
    #     match = {
    #         'teams': {
    #             'faction1': {'faction_id': 'team1', 'name': 'Team A'},
    #             'faction2': {'faction_id': 'team2', 'name': 'Team B'}
    #         }
    #     }
    #     result = get_vetoes.determine_faction(match)
    #     self.assertEqual(result, get_vetoes.FACTION_1_NAME)
    #     self.assertEqual(get_vetoes.team_data['team'], 'Team A')

    # def test_get_faceit_url(self):
    #     match = {'faceit_url': 'https://www.faceit.com/{lang}/match'}
    #     result = get_vetoes.get_faceit_url(match)
    #     self.assertEqual(result, 'https://www.faceit.com/en/match')

    #     match = {}
    #     result = get_vetoes.get_faceit_url(match)
    #     self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()