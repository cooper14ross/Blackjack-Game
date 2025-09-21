from flask import Flask, render_template, jsonify, session, request
import random
from dataclasses import dataclass, asdict, field

app = Flask(__name__)
# In production, set this via environment variable. For local dev this is fine.
app.secret_key = "change-me-please"

SUITS = ["Spades", "Clubs", "Hearts", "Diamonds"]
RANKS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]

@dataclass
class GameState:
    deck: list = field(default_factory=list)
    dealt_index: int = 0
    dealer_hand: list = field(default_factory=list)
    player_hand: list = field(default_factory=list)
    game_over: bool = False
    game_result: str = ""

    def serialize(self):
        return asdict(self)

    @staticmethod
    def deserialize(data):
        gs = GameState()
        gs.deck = data.get("deck", [])
        gs.dealt_index = data.get("dealt_index", 0)
        gs.dealer_hand = data.get("dealer_hand", [])
        gs.player_hand = data.get("player_hand", [])
        gs.game_over = data.get("game_over", False)
        gs.game_result = data.get("game_result", "")
        return gs

def build_deck():
    return [f"{rank} of {suit}" for suit in SUITS for rank in RANKS]

def shuffle_deck(deck):
    random.shuffle(deck)

def deal_card(state: GameState):
    if state.dealt_index >= len(state.deck):
        # reshuffle if we ever run out
        state.deck = build_deck()
        shuffle_deck(state.deck)
        state.dealt_index = 0
    card = state.deck[state.dealt_index]
    state.dealt_index += 1
    return card

def calc_hand_value(hand):
    value = 0
    ace_count = 0
    for card in hand:
        rank = card.split(" ")[0]
        if rank == "A":
            value += 11
            ace_count += 1
        elif rank in ["J", "Q", "K"]:
            value += 10
        else:
            value += int(rank)
    # downgrade aces if bust
    while value > 21 and ace_count > 0:
        value -= 10
        ace_count -= 1
    return value

def new_game_state():
    state = GameState()
    state.deck = build_deck()
    shuffle_deck(state.deck)
    # Deal like your Processing sketch: player gets two, dealer gets one
    state.player_hand.append(deal_card(state))
    state.player_hand.append(deal_card(state))
    state.dealer_hand.append(deal_card(state))
    state.game_over = False
    state.game_result = ""
    return state

def load_state():
    raw = session.get("game_state")
    if not raw:
        s = new_game_state()
        session["game_state"] = s.serialize()
        return s
    return GameState.deserialize(raw)

def save_state(state: GameState):
    session["game_state"] = state.serialize()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/state")
def api_state():
    state = load_state()
    return jsonify({
        "dealerHand": state.dealer_hand,
        "playerHand": state.player_hand,
        "dealerValue": calc_hand_value(state.dealer_hand),
        "playerValue": calc_hand_value(state.player_hand),
        "gameOver": state.game_over,
        "gameResult": state.game_result,
    })

@app.route("/api/new", methods=["POST"])
def api_new():
    state = new_game_state()
    save_state(state)
    return jsonify({"ok": True})

@app.route("/api/hit", methods=["POST"])
def api_hit():
    state = load_state()
    if state.game_over:
        return jsonify({"ok": False, "error": "Game already over"}), 400
    state.player_hand.append(deal_card(state))
    player_value = calc_hand_value(state.player_hand)
    if player_value > 21:
        state.game_over = True
        state.game_result = "Bust! Dealer wins."
    save_state(state)
    return jsonify({"ok": True, "playerValue": player_value})

@app.route("/api/stand", methods=["POST"])
def api_stand():
    state = load_state()
    if state.game_over:
        return jsonify({"ok": False, "error": "Game already over"}), 400

    # Dealer draws until 17 or higher (common rule)
    while calc_hand_value(state.dealer_hand) < 17:
        state.dealer_hand.append(deal_card(state))

    player = calc_hand_value(state.player_hand)
    dealer = calc_hand_value(state.dealer_hand)

    if dealer > 21:
        result = "Dealer busts! You win."
    elif dealer > player:
        result = "Dealer wins."
    elif dealer < player:
        result = "You win!"
    else:
        result = "Push (tie)."

    state.game_over = True
    state.game_result = result
    save_state(state)
    return jsonify({"ok": True, "result": result})

if __name__ == "__main__":
    # Local dev server
    app.run(debug=True)
