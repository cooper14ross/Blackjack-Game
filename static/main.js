async function fetchState() {
  const res = await fetch("/api/state");
  return await res.json();
}

function renderState(s) {
  const dealerHandEl = document.getElementById("dealer-hand");
  const playerHandEl = document.getElementById("player-hand");
  const dealerValueEl = document.getElementById("dealer-value");
  const playerValueEl = document.getElementById("player-value");
  const resultEl = document.getElementById("result");

  dealerHandEl.innerHTML = "";
  playerHandEl.innerHTML = "";

  s.dealerHand.forEach(card => {
    const li = document.createElement("li");
    li.textContent = card;
    dealerHandEl.appendChild(li);
  });
  s.playerHand.forEach(card => {
    const li = document.createElement("li");
    li.textContent = card;
    playerHandEl.appendChild(li);
  });

  dealerValueEl.textContent = s.dealerValue;
  playerValueEl.textContent = s.playerValue;

  resultEl.textContent = s.gameOver ? s.gameResult : "";
  // disable buttons when game over
  document.getElementById("hit-btn").disabled = s.gameOver;
  document.getElementById("stand-btn").disabled = s.gameOver;
}

async function init() {
  renderState(await fetchState());

  document.getElementById("new-btn").addEventListener("click", async () => {
    await fetch("/api/new", { method: "POST" });
    renderState(await fetchState());
  });
  document.getElementById("hit-btn").addEventListener("click", async () => {
    await fetch("/api/hit", { method: "POST" });
    renderState(await fetchState());
  });
  document.getElementById("stand-btn").addEventListener("click", async () => {
    await fetch("/api/stand", { method: "POST" });
    renderState(await fetchState());
  });
}

init();
