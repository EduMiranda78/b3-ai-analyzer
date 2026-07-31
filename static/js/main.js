"use strict";

const form = document.getElementById("formAnalise");
const tickerInput = document.getElementById("ticker");
const loading = document.getElementById("loading");
const submitButton = form
    ? form.querySelector('button[type="submit"]')
    : null;

function setTicker(valor) {
    if (!tickerInput) {
        return;
    }

    tickerInput.value = valor;
    tickerInput.focus();
}

window.setTicker = setTicker;

if (tickerInput) {
    tickerInput.addEventListener("input", function () {
        tickerInput.value = tickerInput.value
            .toUpperCase()
            .replace(/\s+/g, "");
    });
}

if (form) {
    form.addEventListener("submit", function () {
        if (loading) {
            loading.classList.remove("hidden");
        }

        if (submitButton) {
            submitButton.disabled = true;
            submitButton.textContent = "Gerando relatório...";
        }
    });
}
