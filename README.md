# agent-chat

Chatbot en terminal qui discute avec Claude (modèle **Claude Opus 5.5**) via l'API Anthropic.
Les réponses s'affichent au fur et à mesure, et Claude se souvient de toute la conversation.

```
Chat avec claude-opus-5-5 — /reset pour recommencer, /quit pour quitter.

Vous > Bonjour, peux-tu m'expliquer ce qu'est une API ?
Claude > Bien sûr ! Une API (Application Programming Interface) est...
```

## Prérequis

- **Python 3.10 ou plus récent** (`python --version` pour vérifier)
- **Une clé API Anthropic** : à créer sur [console.anthropic.com](https://console.anthropic.com/)
  (rubrique *API Keys*). L'utilisation est facturée sur votre compte Anthropic.

## Installation

```bash
git clone https://github.com/jyilangomassengo-maker/agent-chat.git
cd agent-chat
```

Optionnel mais conseillé : créer un environnement virtuel.

```bash
python -m venv .venv
source .venv/bin/activate        # macOS / Linux
.venv\Scripts\Activate.ps1       # Windows (PowerShell)
```

Installer la dépendance :

```bash
pip install -r requirements.txt
```

## Configurer la clé API

macOS / Linux :

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

Windows (PowerShell) :

```powershell
$env:ANTHROPIC_API_KEY="sk-ant-..."
```

La variable n'est valable que pour le terminal ouvert. Ne mettez jamais votre clé
dans le code ni dans un fichier commité sur GitHub.

## Lancer le chatbot

```bash
python main.py
```

Tapez votre message puis Entrée.

| Commande | Effet |
| --- | --- |
| `/reset` | Efface l'historique et recommence une conversation |
| `/quit` ou `/exit` | Quitte le programme |
| `Ctrl+C` pendant une réponse | Interrompt la réponse en cours |
| `Ctrl+C` ou `Ctrl+D` à l'invite | Quitte le programme |

## Personnaliser

Les réglages sont en haut de `main.py` :

- `MODEL` : le modèle utilisé (`claude-opus-5-5` par défaut).
- `SYSTEM_PROMPT` : les consignes données à Claude (ton, rôle, langue…).
- `EFFORT` : la profondeur de réflexion — `"low"` (rapide, idéal pour discuter),
  `"medium"` ou `"high"` (plus lent mais meilleur sur les questions difficiles).

## Fonctionnement

- Chaque message est envoyé avec tout l'historique de la conversation, en streaming.
- Si un filtre de sécurité refuse une requête à tort, l'API relance automatiquement
  la question sur un modèle de repli (option `fallbacks="default"`).
- Les erreurs (clé invalide, limite de requêtes, réseau) sont affichées clairement ;
  sauf pour une clé invalide, vous pouvez simplement reposer votre question.

## Dépannage

| Message | Solution |
| --- | --- |
| `Clé API invalide ou absente` | Vérifiez que `ANTHROPIC_API_KEY` est bien définie dans ce terminal |
| `ModuleNotFoundError: No module named 'anthropic'` | Lancez `pip install -r requirements.txt` (dans l'environnement virtuel s'il est activé) |
| `Limite de requêtes atteinte` | Attendez quelques secondes et réessayez |
| `Connexion impossible à l'API` | Vérifiez votre connexion internet |
