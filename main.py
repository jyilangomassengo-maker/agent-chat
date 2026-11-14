"""Chatbot en terminal avec l'API Claude.

Usage :
    export ANTHROPIC_API_KEY=sk-ant-...
    python main.py

Commandes pendant la conversation :
    /reset   efface l'historique
    /quit    quitte (ou Ctrl+D / Ctrl+C)
"""

import sys

import anthropic

MODEL = "claude-opus-5-5"
SYSTEM_PROMPT = (
    "Tu es un assistant conversationnel utile et concis. "
    "Réponds dans la langue de l'utilisateur."
)
# Effort de réflexion : "low" convient bien à une conversation, monter à
# "medium"/"high" pour des questions plus difficiles.
EFFORT = "low"


def history_content(content):
    """Prépare le contenu d'une réponse pour le renvoyer dans l'historique.

    Après une bascule vers le modèle de repli, les blocs de réflexion et
    d'appel d'outil situés avant le dernier bloc `fallback` ne doivent pas être
    renvoyés ; le bloc `fallback` lui-même reste à sa place.
    """
    blocks = [block.model_dump(exclude_none=True) for block in content]
    last_fallback = max(
        (i for i, b in enumerate(blocks) if b["type"] == "fallback"), default=-1
    )
    dropped = {"thinking", "redacted_thinking", "tool_use"}
    return [
        b for i, b in enumerate(blocks)
        if not (i < last_fallback and b["type"] in dropped)
    ]


def ask(client, messages):
    """Envoie la conversation et affiche la réponse au fil de l'eau."""
    with client.beta.messages.stream(
        model=MODEL,
        max_tokens=64000,
        system=SYSTEM_PROMPT,
        output_config={"effort": EFFORT},
        # Si un filtre de sécurité refuse la requête, l'API relance
        # automatiquement sur un modèle de repli adapté.
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
        messages=messages,
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
        return stream.get_final_message()


def main():
    try:
        client = anthropic.Anthropic()
    except anthropic.AnthropicError as e:
        sys.exit(f"Impossible de créer le client : {e}\n"
                 "Définissez ANTHROPIC_API_KEY (ou lancez `ant auth login`).")

    messages = []
    print(f"Chat avec {MODEL} — /reset pour recommencer, /quit pour quitter.\n")

    while True:
        try:
            user_input = input("Vous > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nAu revoir !")
            break

        if not user_input:
            continue
        if user_input in ("/quit", "/exit"):
            print("Au revoir !")
            break
        if user_input == "/reset":
            messages.clear()
            print("(historique effacé)\n")
            continue

        messages.append({"role": "user", "content": user_input})
        print("Claude > ", end="", flush=True)

        try:
            response = ask(client, messages)
        except KeyboardInterrupt:
            print("\n(réponse interrompue)\n")
            messages.pop()
            continue
        except anthropic.AuthenticationError:
            sys.exit("\nClé API invalide ou absente (ANTHROPIC_API_KEY).")
        except anthropic.RateLimitError:
            print("\n[Limite de requêtes atteinte, réessayez dans un instant.]\n")
            messages.pop()
            continue
        except anthropic.APIStatusError as e:
            print(f"\n[Erreur API {e.status_code} : {e.message}]\n")
            messages.pop()
            continue
        except anthropic.APIConnectionError:
            print("\n[Connexion impossible à l'API, vérifiez le réseau.]\n")
            messages.pop()
            continue

        print("\n")

        if response.stop_reason == "refusal":
            print("[Requête refusée par les filtres de sécurité.]\n")
            messages.pop()
            continue
        if response.stop_reason == "max_tokens":
            print("[Réponse tronquée : limite de tokens atteinte.]\n")

        # On garde le contenu complet (dont les blocs de réflexion) pour que
        # la conversation reste valide d'un tour à l'autre.
        messages.append(
            {"role": "assistant", "content": history_content(response.content)}
        )


if __name__ == "__main__":
    main()
