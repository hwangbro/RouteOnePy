import unittest

import data

class TestTrainer(unittest.TestCase):
    trainers = data.get_trainers()

    def test_poke_list(self):
        exp_list = 'L58 Gyarados, L56 Dragonair, L56 Dragonair, L60 Aerodactyl, L62 Dragonite'
        self.assertEqual(TestTrainer.trainers['y'][0x3A5A6].poke_list, exp_list)

    def test_prize_money(self):
        self.assertEqual(TestTrainer.trainers['y'][0x3A5A6].prize_money, 6138)

    def test_repr(self):
        exp_str = 'LANCE (0x3a5a6: '
        exp_str += 'L58 Gyarados, L56 Dragonair, L56 Dragonair, L60 Aerodactyl, L62 Dragonite'
        exp_str += ') Prize 6138'
        self.assertEqual(str(TestTrainer.trainers['y'][0x3A5A6]), exp_str)

    def test_set_move(self):
        y_lance = TestTrainer.trainers['y'][0x3a5a6]
        tackle = data.get_move('tackle')
        self.assertEqual(y_lance.pokes[0].moveset[0].name, 'Dragon Rage')
        y_lance.set_move(1, 1, tackle)
        self.assertEqual(y_lance.pokes[0].moveset[0].name, 'Tackle')

        rb_lance = TestTrainer.trainers['rb'][0x3a522]
        self.assertEqual(rb_lance.pokes[0].moveset[0].name, 'Dragon Rage')
        rb_lance.set_move(0, 0, tackle, False)
        self.assertEqual(rb_lance.pokes[0].moveset[0].name, 'Tackle')

if __name__ == '__main__':
    unittest.main()
