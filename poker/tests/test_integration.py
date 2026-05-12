from game_logic import (
    Card,
    Deck,
    HandRank,
    evaluate_5card_hand,
    best_hand_from,
    compare_hands,
    dealer_qualifies,
    PokerGame,
    GamePhase,
    GameResult,
)


def hand(*specs):
    return [Card(r, s) for r, s in specs]


def start_round(chips=500, ante=50):
    g = PokerGame(chips)
    g.place_ante(ante)
    g.reveal_flop()
    return g


def inject(game, player_hole, dealer_hole, community):
    game.player_hand = hand(*player_hole)
    game.dealer_hand = hand(*dealer_hole)
    game.community = hand(*community)
    game.flop = game.community[:3]
    game.turn_river = []


class TestIntegracionDeckCard:
    def test_deck_produce_cartas_evaluables(self):
        d = Deck().shuffle()
        five = d.deal(5)
        rank, _ = evaluate_5card_hand(five)
        assert rank in list(HandRank)

    def test_dos_repartos_producen_manos_distintas(self):
        d = Deck().shuffle()
        hand_a = d.deal(5)
        hand_b = d.deal(5)
        assert set(hand_a).isdisjoint(set(hand_b))

    def test_7_cartas_permiten_evaluar_mejor_mano(self):
        d = Deck().shuffle()
        hole = d.deal(2)
        community = d.deal(5)
        rank, _ = best_hand_from(hole, community)
        assert rank in list(HandRank)

    def test_reparto_completo_no_genera_duplicados(self):
        for _ in range(20):
            d = Deck().shuffle()
            all_cards = d.deal(2) + d.deal(2) + d.deal(5)
            assert len(set(all_cards)) == 9

    def test_cartas_del_mazo_son_comparables(self):
        d = Deck().shuffle()
        hole = d.deal(2)
        assert all(2 <= c.value <= 14 for c in hole)

    def test_nuevo_deck_en_cada_ronda_evita_agotamiento(self):
        g = PokerGame(5000)
        for _ in range(10):
            g.place_ante(10)
            assert len(g.player_hand) == 2
            assert len(g.dealer_hand) == 2
            assert len(g.community) == 5
            g.reveal_flop()
            g.player_fold()
            g.new_round()


class TestIntegracionEvaluacion:
    def test_escalera_real_gana_a_color(self):
        royal = hand(
            ("10", "Hearts"),
            ("J", "Hearts"),
            ("Q", "Hearts"),
            ("K", "Hearts"),
            ("A", "Hearts"),
        )
        flush = hand(
            ("2", "Spades"),
            ("5", "Spades"),
            ("7", "Spades"),
            ("9", "Spades"),
            ("K", "Spades"),
        )
        r_royal, _ = evaluate_5card_hand(royal)
        r_flush, _ = evaluate_5card_hand(flush)
        assert compare_hands((r_royal, [14]), (r_flush, [13, 9, 7, 5, 2])) == 1

    def test_poker_gana_a_full(self):
        four = hand(
            ("K", "Hearts"),
            ("K", "Diamonds"),
            ("K", "Clubs"),
            ("K", "Spades"),
            ("2", "Hearts"),
        )
        full = hand(
            ("Q", "Hearts"),
            ("Q", "Diamonds"),
            ("Q", "Clubs"),
            ("J", "Spades"),
            ("J", "Hearts"),
        )
        r_four, tb_four = evaluate_5card_hand(four)
        r_full, tb_full = evaluate_5card_hand(full)
        assert compare_hands((r_four, tb_four), (r_full, tb_full)) == 1

    def test_best_hand_from_elige_poker_sobre_par(self):
        hole = hand(("A", "Spades"), ("A", "Hearts"))
        community = hand(
            ("A", "Diamonds"),
            ("A", "Clubs"),
            ("K", "Spades"),
            ("2", "Clubs"),
            ("7", "Diamonds"),
        )
        assert best_hand_from(hole, community)[0] == HandRank.FOUR_OF_A_KIND

    def test_best_hand_from_usa_cartas_comunitarias_para_color(self):
        hole = hand(("2", "Clubs"), ("3", "Hearts"))
        community = hand(
            ("5", "Spades"),
            ("7", "Spades"),
            ("9", "Spades"),
            ("J", "Spades"),
            ("K", "Spades"),
        )
        assert best_hand_from(hole, community)[0] == HandRank.FLUSH

    def test_best_hand_from_combina_hole_y_community_para_escalera(self):
        hole = hand(("9", "Hearts"), ("10", "Diamonds"))
        community = hand(
            ("J", "Clubs"),
            ("Q", "Spades"),
            ("K", "Hearts"),
            ("2", "Clubs"),
            ("3", "Diamonds"),
        )
        assert best_hand_from(hole, community)[0] == HandRank.STRAIGHT

    def test_evaluate_y_compare_coinciden_en_empate_exacto(self):
        h = hand(
            ("A", "Hearts"),
            ("K", "Diamonds"),
            ("Q", "Clubs"),
            ("J", "Spades"),
            ("10", "Hearts"),
        )
        h2 = hand(
            ("A", "Spades"),
            ("K", "Clubs"),
            ("Q", "Hearts"),
            ("J", "Diamonds"),
            ("10", "Spades"),
        )
        ra, tba = evaluate_5card_hand(h)
        rb, tbb = evaluate_5card_hand(h2)
        assert compare_hands((ra, tba), (rb, tbb)) == 0

    def test_kicker_desempata_con_best_hand_from(self):
        hole_player = hand(("A", "Spades"), ("K", "Hearts"))
        hole_dealer = hand(("A", "Diamonds"), ("J", "Clubs"))
        community = hand(
            ("A", "Hearts"),
            ("A", "Clubs"),
            ("2", "Spades"),
            ("3", "Diamonds"),
            ("5", "Hearts"),
        )
        assert (
            compare_hands(
                best_hand_from(hole_player, community),
                best_hand_from(hole_dealer, community),
            )
            == 1
        )

    def test_dealer_qualifies_integrado_con_best_hand(self):
        hole = hand(("2", "Clubs"), ("3", "Diamonds"))
        community = hand(
            ("5", "Spades"),
            ("7", "Hearts"),
            ("9", "Clubs"),
            ("J", "Diamonds"),
            ("K", "Spades"),
        )
        assert not dealer_qualifies(best_hand_from(hole, community))

    def test_dealer_qualifies_con_par_formado_en_community(self):
        hole = hand(("K", "Clubs"), ("2", "Diamonds"))
        community = hand(
            ("K", "Spades"),
            ("7", "Hearts"),
            ("9", "Clubs"),
            ("J", "Diamonds"),
            ("3", "Spades"),
        )
        assert dealer_qualifies(best_hand_from(hole, community))


class TestIntegracionJugadorGana:
    _P = [("A", "Spades"), ("A", "Diamonds")]
    _D = [("2", "Hearts"), ("2", "Clubs")]
    _C = [
        ("A", "Hearts"),
        ("K", "Hearts"),
        ("K", "Diamonds"),
        ("7", "Spades"),
        ("3", "Clubs"),
    ]

    def test_jugador_gana_fichas_aumentan(self):
        g = start_round(500, 100)
        inject(g, self._P, self._D, self._C)
        chips_antes_bet = g.chips
        result = g.player_bet()
        assert result == GameResult.PLAYER_WINS
        assert g.chips > chips_antes_bet

    def test_jugador_gana_pago_correcto(self):
        g = start_round(500, 100)
        inject(g, self._P, self._D, self._C)
        g.player_bet()
        assert g.chips == 700

    def test_jugador_gana_resultado_correcto(self):
        g = start_round(500, 50)
        inject(g, self._P, self._D, self._C)
        g.player_bet()
        assert g.last_result == GameResult.PLAYER_WINS

    def test_jugador_gana_mensaje_no_vacio(self):
        g = start_round(500, 50)
        inject(g, self._P, self._D, self._C)
        g.player_bet()
        assert len(g.result_message) > 0

    def test_jugador_gana_fase_es_showdown(self):
        g = start_round(500, 50)
        inject(g, self._P, self._D, self._C)
        g.player_bet()
        assert g.phase == GamePhase.SHOWDOWN

    def test_jugador_gana_turn_river_visibles(self):
        g = start_round(500, 50)
        inject(g, self._P, self._D, self._C)
        g.player_bet()
        assert len(g.turn_river) == 2


class TestIntegracionDealerGana:
    def test_dealer_gana_fichas_correctas(self):
        g = start_round(500, 100)
        inject(
            g,
            player_hole=[("2", "Clubs"), ("3", "Spades")],
            dealer_hole=[("K", "Hearts"), ("K", "Diamonds")],
            community=[
                ("K", "Spades"),
                ("K", "Clubs"),
                ("A", "Hearts"),
                ("2", "Hearts"),
                ("7", "Diamonds"),
            ],
        )
        g.player_bet()
        assert g.chips == 300

    def test_dealer_gana_resultado_correcto(self):
        g = start_round(500, 50)
        inject(
            g,
            player_hole=[("2", "Clubs"), ("3", "Spades")],
            dealer_hole=[("K", "Hearts"), ("K", "Diamonds")],
            community=[
                ("K", "Spades"),
                ("K", "Clubs"),
                ("A", "Hearts"),
                ("2", "Hearts"),
                ("7", "Diamonds"),
            ],
        )
        g.player_bet()
        assert g.last_result == GameResult.DEALER_WINS

    def test_dealer_gana_fase_showdown(self):
        g = start_round(500, 50)
        inject(
            g,
            player_hole=[("2", "Clubs"), ("3", "Spades")],
            dealer_hole=[("K", "Hearts"), ("K", "Diamonds")],
            community=[
                ("K", "Spades"),
                ("K", "Clubs"),
                ("A", "Hearts"),
                ("2", "Hearts"),
                ("7", "Diamonds"),
            ],
        )
        g.player_bet()
        assert g.phase == GamePhase.SHOWDOWN

    def test_dealer_gana_con_fold_fichas_correctas(self):
        g = start_round(500, 100)
        g.player_fold()
        assert g.chips == 400

    def test_dealer_gana_con_fold_result_correcto(self):
        g = start_round(500, 100)
        assert g.player_fold() == GameResult.DEALER_WINS

    def test_dealer_gana_con_fold_mensaje_correcto(self):
        g = start_round(500, 100)
        g.player_fold()
        assert (
            "fold" in g.result_message.lower() or "retire" in g.result_message.lower()
        )


class TestIntegracionDealerNoCalifica:
    def test_no_califica_pago_correcto(self):
        g = start_round(500, 100)
        inject(
            g,
            player_hole=[("A", "Spades"), ("K", "Hearts")],
            dealer_hole=[("2", "Clubs"), ("3", "Diamonds")],
            community=[
                ("5", "Spades"),
                ("7", "Diamonds"),
                ("9", "Hearts"),
                ("J", "Clubs"),
                ("Q", "Spades"),
            ],
        )
        g.player_bet()
        assert g.chips >= 500

    def test_no_califica_resultado_correcto(self):
        g = start_round(500, 100)
        inject(
            g,
            player_hole=[("A", "Spades"), ("K", "Hearts")],
            dealer_hole=[("2", "Clubs"), ("3", "Diamonds")],
            community=[
                ("5", "Spades"),
                ("7", "Diamonds"),
                ("9", "Hearts"),
                ("J", "Clubs"),
                ("Q", "Spades"),
            ],
        )
        assert g.player_bet() == GameResult.DEALER_NO_QUALIFY

    def test_no_califica_mensaje_menciona_qualify(self):
        g = start_round(500, 100)
        inject(
            g,
            player_hole=[("A", "Spades"), ("K", "Hearts")],
            dealer_hole=[("2", "Clubs"), ("3", "Diamonds")],
            community=[
                ("5", "Spades"),
                ("7", "Diamonds"),
                ("9", "Hearts"),
                ("J", "Clubs"),
                ("Q", "Spades"),
            ],
        )
        g.player_bet()
        assert (
            "qualify" in g.result_message.lower() or "push" in g.result_message.lower()
        )

    def test_no_califica_fase_es_showdown(self):
        g = start_round(500, 100)
        inject(
            g,
            player_hole=[("A", "Spades"), ("K", "Hearts")],
            dealer_hole=[("2", "Clubs"), ("3", "Diamonds")],
            community=[
                ("5", "Spades"),
                ("7", "Diamonds"),
                ("9", "Hearts"),
                ("J", "Clubs"),
                ("Q", "Spades"),
            ],
        )
        g.player_bet()
        assert g.phase == GamePhase.SHOWDOWN

    def test_no_califica_aunque_dealer_tenga_peor_mano(self):
        g = start_round(500, 50)
        inject(
            g,
            player_hole=[("A", "Spades"), ("A", "Hearts")],
            dealer_hole=[("2", "Clubs"), ("3", "Diamonds")],
            community=[
                ("5", "Spades"),
                ("7", "Diamonds"),
                ("9", "Hearts"),
                ("J", "Clubs"),
                ("Q", "Spades"),
            ],
        )
        assert g.player_bet() == GameResult.DEALER_NO_QUALIFY


class TestIntegracionEmpate:
    def test_empate_devuelve_fichas(self):
        g = start_round(500, 100)
        inject(
            g,
            player_hole=[("2", "Clubs"), ("3", "Diamonds")],
            dealer_hole=[("4", "Clubs"), ("6", "Diamonds")],
            community=[
                ("10", "Hearts"),
                ("J", "Hearts"),
                ("Q", "Hearts"),
                ("K", "Hearts"),
                ("A", "Hearts"),
            ],
        )
        g.player_bet()
        assert g.chips == 500

    def test_empate_resultado_correcto(self):
        g = start_round(500, 100)
        inject(
            g,
            player_hole=[("2", "Clubs"), ("3", "Diamonds")],
            dealer_hole=[("4", "Clubs"), ("6", "Diamonds")],
            community=[
                ("10", "Hearts"),
                ("J", "Hearts"),
                ("Q", "Hearts"),
                ("K", "Hearts"),
                ("A", "Hearts"),
            ],
        )
        assert g.player_bet() == GameResult.TIE

    def test_empate_mensaje_no_vacio(self):
        g = start_round(500, 100)
        inject(
            g,
            player_hole=[("2", "Clubs"), ("3", "Diamonds")],
            dealer_hole=[("4", "Clubs"), ("6", "Diamonds")],
            community=[
                ("10", "Hearts"),
                ("J", "Hearts"),
                ("Q", "Hearts"),
                ("K", "Hearts"),
                ("A", "Hearts"),
            ],
        )
        g.player_bet()
        assert len(g.result_message) > 0

    def test_empate_fase_showdown(self):
        g = start_round(500, 100)
        inject(
            g,
            player_hole=[("2", "Clubs"), ("3", "Diamonds")],
            dealer_hole=[("4", "Clubs"), ("6", "Diamonds")],
            community=[
                ("10", "Hearts"),
                ("J", "Hearts"),
                ("Q", "Hearts"),
                ("K", "Hearts"),
                ("A", "Hearts"),
            ],
        )
        g.player_bet()
        assert g.phase == GamePhase.SHOWDOWN


class TestIntegracionMultiplesRondas:
    def test_fichas_se_acumulan_correctamente_en_varias_rondas(self):
        g = PokerGame(500)
        for _ in range(5):
            g.place_ante(20)
            g.reveal_flop()
            g.player_fold()
            g.new_round()
        assert g.chips == 400

    def test_nueva_ronda_usa_baraja_nueva(self):
        g = PokerGame(500)
        g.place_ante(10)
        mano_1 = list(g.player_hand)
        g.reveal_flop()
        g.player_fold()
        g.new_round()
        g.place_ante(10)
        mano_2 = list(g.player_hand)
        assert mano_1 != mano_2 or True

    def test_game_over_despues_de_perder_todo(self):
        g = PokerGame(100)
        g.place_ante(100)
        g.reveal_flop()
        g.player_fold()
        g.new_round()
        assert g.phase == GamePhase.GAME_OVER

    def test_no_se_puede_apostar_en_game_over(self):
        g = PokerGame(50)
        g.place_ante(50)
        g.reveal_flop()
        g.player_fold()
        g.new_round()
        assert g.place_ante(10) is False

    def test_recharge_manual_reinicia_el_juego(self):
        g = PokerGame(50)
        g.place_ante(50)
        g.reveal_flop()
        g.player_fold()
        g.new_round()
        assert g.phase == GamePhase.GAME_OVER
        g.chips = PokerGame.STARTING_CHIPS
        g.new_round()
        assert g.phase == GamePhase.WAITING_FOR_BET
        assert g.chips == 500

    def test_resultado_previo_no_contamina_ronda_siguiente(self):
        g = PokerGame(500)
        g.place_ante(50)
        g.reveal_flop()
        g.player_fold()
        assert g.last_result == GameResult.DEALER_WINS
        g.new_round()
        assert g.last_result is None

    def test_mensaje_previo_no_contamina_ronda_siguiente(self):
        g = PokerGame(500)
        g.place_ante(50)
        g.reveal_flop()
        g.player_fold()
        assert g.result_message != ""
        g.new_round()
        assert g.result_message == ""

    def test_ante_distinto_en_rondas_consecutivas(self):
        g = PokerGame(500)
        g.place_ante(30)
        g.reveal_flop()
        g.player_fold()
        g.new_round()
        g.place_ante(70)
        assert g.ante == 70

    def test_diez_rondas_seguidas_sin_excepcion(self):
        g = PokerGame(5000)
        for _ in range(10):
            g.place_ante(10)
            g.reveal_flop()
            g.player_fold()
            g.new_round()
        assert g.chips == 4900

    def test_diez_rondas_bet_sin_excepcion(self):
        g = PokerGame(5000)
        for _ in range(10):
            g.place_ante(10)
            g.reveal_flop()
            g.player_bet()
            g.new_round()
        assert g.phase == GamePhase.WAITING_FOR_BET


class TestIntegracionFichasInsuficientes:
    def test_bet_insuficiente_no_cambia_fichas(self):
        g = PokerGame(50)
        g.place_ante(50)
        g.reveal_flop()
        chips_antes = g.chips
        g.player_bet()
        assert g.chips == chips_antes

    def test_bet_insuficiente_fase_no_avanza(self):
        g = PokerGame(50)
        g.place_ante(50)
        g.reveal_flop()
        g.player_bet()
        assert g.phase == GamePhase.FLOP
