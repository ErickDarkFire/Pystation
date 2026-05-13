import pygame
from unittest.mock import patch
from behave import given, when, then
from models.card import Card


def simulate_click(context, x, y):
    """Simula un click del mouse en una coordenada x, y"""
    with patch("pygame.mouse.get_pos", return_value=(x, y)):
        event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": (x, y), "button": 1})

        if context.game.state == "BETTING":
            for r, v in context.game.chip_rects:
                if r.collidepoint(event.pos) and context.game.player.money >= v:
                    context.game.player.money -= v
                    context.game.player.current_bet += v

        context.game.update([event])


@given('el estado del juego es "{state}" y la apuesta actual es {bet:d}')
def step_initial_state_betting(context, state, bet):
    assert context.game.state == state
    assert context.game.player.current_bet == bet


@given("el mazo tiene las cartas preparadas para repartir inicialmente")
def step_mazo_preparado_inicial(context):
    context.game.shoe.cards = [
        Card("♠", "10"),
        Card("♥", "10"),
        Card("♦", "9"),
        Card("♣", "9"),
    ]


@when("el usuario hace clic en la ficha de ${amount:d}")
def step_click_chip(context, amount):
    # En nuestro mock de test, la primera ficha es la de 10
    ficha_rect = context.game.chip_rects[0][0]
    simulate_click(context, ficha_rect.centerx, ficha_rect.centery)


@when("hace clic en el botón DEAL")
def step_click_deal(context):
    simulate_click(
        context, context.game.btn_deal.rect.centerx, context.game.btn_deal.rect.centery
    )


@then("la apuesta actual es {bet:d}")
def step_check_bet(context, bet):
    assert context.game.player.current_bet == bet


@then('el estado del juego cambia a "{state}"')
def step_check_state_change(context, state):
    assert context.game.state == state


@then("el jugador tiene {count:d} cartas")
def step_check_player_card_count(context, count):
    assert len(context.game.player.hand) == count


@then("el crupier tiene {count:d} cartas")
def step_check_dealer_card_count(context, count):
    assert len(context.game.dealer.hand) == count


@given("una apuesta válida de {bet:d}")
def step_valid_bet(context, bet):
    context.game.player.current_bet = bet
    context.game.state = "BETTING"


@given("el mazo está preparado para que el jugador saque un 20 y luego un 5")
def step_mazo_preparado_bust(context):
    context.game.shoe.cards = [
        Card("♠", "5"),  # Carta extra para el Hit
        Card("♠", "9"),  # Dealer 2
        Card("♥", "10"),  # Player 2
        Card("♦", "9"),  # Dealer 1
        Card("♣", "10"),  # Player 1
    ]


@when("se reparten las cartas")
def step_deal_cards(context):
    simulate_click(
        context, context.game.btn_deal.rect.centerx, context.game.btn_deal.rect.centery
    )
    assert context.game.state == "PLAYING"


@when("el jugador hace clic en el botón HIT")
def step_click_hit(context):
    simulate_click(
        context, context.game.btn_hit.rect.centerx, context.game.btn_hit.rect.centery
    )


@then('el mensaje principal es "{msg}"')
def step_check_main_message(context, msg):
    assert context.game.msg_main == msg


@given("una apuesta válida de {bet:d} y saldo de {money:d}")
def step_valid_bet_with_money(context, bet, money):
    context.game.player.current_bet = bet
    context.game.player.money = money
    context.game.state = "BETTING"


@given("el mazo está preparado para que el jugador tenga 20 y el crupier 17")
def step_mazo_preparado_win(context):
    context.game.shoe.cards = [
        Card("♠", "7"),  # Dealer 2
        Card("♥", "10"),  # Player 2
        Card("♦", "10"),  # Dealer 1
        Card("♣", "10"),  # Player 1
    ]


@when("el jugador hace clic en el botón STAND")
def step_click_stand(context):
    simulate_click(
        context,
        context.game.btn_stand.rect.centerx,
        context.game.btn_stand.rect.centery,
    )
    event_dummy = pygame.event.Event(pygame.MOUSEMOTION, {"pos": (0, 0)})
    context.game.update([event_dummy])


@then("el saldo del jugador aumenta a {money:d}")
def step_check_money_increase(context, money):
    assert context.game.player.money == money
