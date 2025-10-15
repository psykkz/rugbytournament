from flask import Flask, render_template_string, request, jsonify, send_file
from itertools import combinations
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import cm
import io
import random

app = Flask(__name__)

# Template HTML
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gestionnaire de Tournoi de Rugby</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #2d5016 0%, #4a7c2e 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }
        h1 {
            color: #2d5016;
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.5em;
        }
        .rugby-icon {
            font-size: 3em;
            text-align: center;
            margin-bottom: 20px;
        }
        .section {
            margin-bottom: 30px;
        }
        .section h2 {
            color: #4a7c2e;
            margin-bottom: 15px;
            font-size: 1.5em;
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
            color: #333;
        }
        input[type="number"], input[type="text"], select {
            width: 100%;
            padding: 10px;
            border: 2px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        input:focus, select:focus {
            outline: none;
            border-color: #4a7c2e;
        }
        button {
            background: linear-gradient(135deg, #2d5016 0%, #4a7c2e 100%);
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 5px;
            font-size: 16px;
            cursor: pointer;
            transition: transform 0.2s;
        }
        button:hover {
            transform: translateY(-2px);
        }
        button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        .poule-section {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .poule-section h3 {
            color: #2d5016;
            margin-bottom: 15px;
        }
        .team-input-group {
            display: flex;
            gap: 10px;
            margin-bottom: 10px;
        }
        .team-input-group input {
            flex: 1;
        }
        .team-input-group button {
            padding: 10px 20px;
        }
        .teams-list {
            margin-top: 10px;
        }
        .team-tag {
            display: inline-block;
            background: #2d5016;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            margin: 5px;
            font-size: 14px;
        }
        .matches-section {
            margin-top: 30px;
        }
        .terrain {
            background: white;
            border: 2px solid #4a7c2e;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
        }
        .terrain h4 {
            color: #2d5016;
            margin-bottom: 10px;
        }
        .match {
            background: #e8f5e9;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 10px;
            border-left: 4px solid #4a7c2e;
        }
        .match.completed {
            background: #c8e6c9;
            border-left-color: #2d5016;
        }
        .match-header {
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 10px;
        }
        .match-number {
            font-weight: bold;
            color: #2d5016;
        }
        .match-teams {
            flex: 1;
            font-weight: 500;
        }
        .match-checkbox {
            transform: scale(1.5);
            cursor: pointer;
        }
        .score-inputs {
            display: flex;
            gap: 10px;
            align-items: center;
            margin-top: 10px;
        }
        .score-inputs input {
            width: 70px;
            padding: 5px;
            text-align: center;
        }
        .score-inputs button {
            padding: 5px 15px;
            font-size: 14px;
        }
        .hidden {
            display: none;
        }
        .classements-section {
            margin-top: 40px;
        }
        .classement-poule {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .classement-poule h3 {
            color: #2d5016;
            margin-bottom: 15px;
        }
        .classement-table {
            width: 100%;
            border-collapse: collapse;
        }
        .classement-table th {
            background: #2d5016;
            color: white;
            padding: 10px;
            text-align: left;
        }
        .classement-table td {
            padding: 10px;
            border-bottom: 1px solid #ddd;
        }
        .classement-table tr:hover {
            background: #e8f5e9;
        }
        .export-btn {
            position: fixed;
            bottom: 30px;
            right: 30px;
            background: #2d5016;
            font-size: 18px;
            padding: 15px 30px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
            z-index: 1000;
        }
        .alert {
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .alert-info {
            background: #d1ecf1;
            color: #0c5460;
            border: 1px solid #bee5eb;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="rugby-icon">🏉</div>
        <h1>Gestionnaire de Tournoi de Rugby</h1>
        
        <div id="config-section" class="section">
            <h2>Configuration du tournoi</h2>
            <div class="form-group">
                <label for="nbPoules">Nombre de poules :</label>
                <input type="number" id="nbPoules" min="1" max="10" value="2">
            </div>
            <div class="form-group">
                <label for="nommerPoules">Nommer les poules ?</label>
                <select id="nommerPoules">
                    <option value="non">Non (Poule 1, Poule 2...)</option>
                    <option value="oui">Oui (personnalisé)</option>
                </select>
            </div>
            <div id="nomsPoules" class="hidden"></div>
            <div class="form-group">
                <label for="nbTerrains">Nombre de terrains :</label>
                <input type="number" id="nbTerrains" min="1" max="10" value="2">
            </div>
            <button id="btnValider">Valider la configuration</button>
        </div>
        
        <div id="poules-section" class="section hidden">
            <h2>Équipes par poule</h2>
            <div id="poulesContainer"></div>
        </div>
        
        <div id="matches-section" class="section hidden matches-section">
            <h2>Planning des matchs</h2>
            <div id="matchesContainer"></div>
        </div>
        
        <div id="classements-section" class="section hidden classements-section">
            <h2>Classements</h2>
            <div id="classementsContainer"></div>
        </div>
    </div>
    
    <button id="exportBtn" class="export-btn hidden">📄 Exporter en PDF</button>
    
    <script>
        var config = {
            nbPoules: 2,
            nommerPoules: false,
            nomsPoules: [],
            nbTerrains: 2,
            poules: []
        };
        
        var matchsData = {};
        
        document.addEventListener('DOMContentLoaded', function() {
            document.getElementById('nommerPoules').addEventListener('change', function() {
                var nomsDiv = document.getElementById('nomsPoules');
                if (this.value === 'oui') {
                    nomsDiv.classList.remove('hidden');
                    updateNomsPoules();
                } else {
                    nomsDiv.classList.add('hidden');
                }
            });
            
            document.getElementById('nbPoules').addEventListener('change', function() {
                if (document.getElementById('nommerPoules').value === 'oui') {
                    updateNomsPoules();
                }
            });
            
            document.getElementById('btnValider').addEventListener('click', validerConfig);
            document.getElementById('exportBtn').addEventListener('click', exportPDF);
        });
        
        function updateNomsPoules() {
            var nbPoules = parseInt(document.getElementById('nbPoules').value);
            var nomsDiv = document.getElementById('nomsPoules');
            var html = '<div class="alert alert-info">Entrez un nom pour chaque poule :</div>';
            for (var i = 0; i < nbPoules; i++) {
                html += '<div class="form-group">';
                html += '<label for="nomPoule' + i + '">Nom de la poule ' + (i + 1) + ' :</label>';
                html += '<input type="text" id="nomPoule' + i + '" placeholder="Ex: Groupe A, Seniors...">';
                html += '</div>';
            }
            nomsDiv.innerHTML = html;
        }
        
        function validerConfig() {
            config.nbPoules = parseInt(document.getElementById('nbPoules').value);
            config.nbTerrains = parseInt(document.getElementById('nbTerrains').value);
            config.nommerPoules = document.getElementById('nommerPoules').value === 'oui';
            
            if (config.nommerPoules) {
                config.nomsPoules = [];
                for (var i = 0; i < config.nbPoules; i++) {
                    var input = document.getElementById('nomPoule' + i);
                    var nom = input ? input.value.trim() : '';
                    config.nomsPoules.push(nom || 'Poule ' + (i + 1));
                }
            } else {
                config.nomsPoules = [];
                for (var i = 0; i < config.nbPoules; i++) {
                    config.nomsPoules.push('Poule ' + (i + 1));
                }
            }
            
            config.poules = [];
            for (var i = 0; i < config.nomsPoules.length; i++) {
                config.poules.push({ nom: config.nomsPoules[i], equipes: [] });
            }
            
            document.getElementById('config-section').classList.add('hidden');
            document.getElementById('poules-section').classList.remove('hidden');
            afficherPoules();
        }
        
        function afficherPoules() {
            var container = document.getElementById('poulesContainer');
            var html = '';
            for (var i = 0; i < config.poules.length; i++) {
                var poule = config.poules[i];
                html += '<div class="poule-section">';
                html += '<h3>' + poule.nom + '</h3>';
                html += '<div class="team-input-group">';
                html += '<input type="text" class="team-input" data-poule="' + i + '" placeholder="Nom de equipe">';
                html += '<button class="btn-add-team" data-poule="' + i + '">Ajouter</button>';
                html += '</div>';
                html += '<div class="teams-list" id="teamsList' + i + '"></div>';
                html += '</div>';
            }
            container.innerHTML = html;
            
            var buttons = document.querySelectorAll('.btn-add-team');
            for (var i = 0; i < buttons.length; i++) {
                buttons[i].addEventListener('click', function() {
                    var pouleIndex = parseInt(this.getAttribute('data-poule'));
                    ajouterEquipe(pouleIndex);
                });
            }
        }
        
        function ajouterEquipe(pouleIndex) {
            var inputs = document.querySelectorAll('.team-input');
            var input = inputs[pouleIndex];
            var nomEquipe = input.value.trim();
            if (nomEquipe === '') {
                alert('Veuillez entrer un nom');
                return;
            }
            config.poules[pouleIndex].equipes.push(nomEquipe);
            input.value = '';
            afficherEquipesPoule(pouleIndex);
            genererMatchs();
        }
        
        function afficherEquipesPoule(pouleIndex) {
            var list = document.getElementById('teamsList' + pouleIndex);
            var equipes = config.poules[pouleIndex].equipes;
            var html = '';
            for (var i = 0; i < equipes.length; i++) {
                html += '<span class="team-tag">' + equipes[i] + '</span>';
            }
            list.innerHTML = html;
        }
        
        function genererMatchs() {
            var data = {
                poules: config.poules,
                nbTerrains: config.nbTerrains
            };
            
            fetch('/generer_matchs', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            })
            .then(function(response) { return response.json(); })
            .then(function(data) {
                afficherMatchs(data.terrains);
                calculerClassements();
            })
            .catch(function(error) { console.error('Erreur:', error); });
        }
        
        function afficherMatchs(terrains) {
            var section = document.getElementById('matches-section');
            var container = document.getElementById('matchesContainer');
            
            var hasMatchs = false;
            for (var i = 0; i < terrains.length; i++) {
                if (terrains[i].length > 0) {
                    hasMatchs = true;
                    break;
                }
            }
            
            if (!hasMatchs) {
                section.classList.add('hidden');
                document.getElementById('exportBtn').classList.add('hidden');
                return;
            }
            
            section.classList.remove('hidden');
            document.getElementById('exportBtn').classList.remove('hidden');
            
            var html = '';
            for (var i = 0; i < terrains.length; i++) {
                var terrain = terrains[i];
                html += '<div class="terrain">';
                html += '<h4>Terrain ' + (i + 1) + '</h4>';
                
                for (var j = 0; j < terrain.length; j++) {
                    var match = terrain[j];
                    var matchId = 'match_' + i + '_' + j;
                    
                    if (match === null || match === undefined) {
                        html += '<div class="match" style="opacity: 0.5; font-style: italic;">';
                        html += '<span class="match-number">Match ' + (j + 1) + ':</span> Pas de match';
                        html += '</div>';
                    } else {
                        var isCompleted = matchsData[matchId] && matchsData[matchId].completed;
                        var matchClass = isCompleted ? 'match completed' : 'match';
                        
                        html += '<div class="' + matchClass + '" id="' + matchId + '">';
                        html += '<div class="match-header">';
                        html += '<span class="match-number">Match ' + (j + 1) + ':</span>';
                        html += '<span class="match-teams">' + match.equipe1 + ' vs ' + match.equipe2 + '</span>';
                        html += '<span style="color: #888; font-size: 12px;">(' + match.poule + ')</span>';
                        html += '<input type="checkbox" class="match-checkbox" data-matchid="' + matchId + '" ' + (isCompleted ? 'checked' : '') + '>';
                        html += '</div>';
                        html += '<div class="score-inputs ' + (isCompleted ? '' : 'hidden') + '" id="scores_' + matchId + '">';
                        html += '<label>' + match.equipe1 + ':</label>';
                        html += '<input type="number" id="score1_' + matchId + '" min="0" value="' + (matchsData[matchId] ? matchsData[matchId].score1 : 0) + '">';
                        html += '<span>-</span>';
                        html += '<label>' + match.equipe2 + ':</label>';
                        html += '<input type="number" id="score2_' + matchId + '" min="0" value="' + (matchsData[matchId] ? matchsData[matchId].score2 : 0) + '">';
                        html += '<button class="btn-valider-score" data-matchid="' + matchId + '" data-equipe1="' + match.equipe1 + '" data-equipe2="' + match.equipe2 + '" data-poule="' + match.poule + '">Valider</button>';
                        html += '</div>';
                        html += '</div>';
                    }
                }
                html += '</div>';
            }
            container.innerHTML = html;
            
            // Ajouter les event listeners après l'insertion du HTML
            var checkboxes = document.querySelectorAll('.match-checkbox');
            for (var k = 0; k < checkboxes.length; k++) {
                checkboxes[k].addEventListener('change', function() {
                    toggleMatch(this.getAttribute('data-matchid'));
                });
            }
            
            var btnValiders = document.querySelectorAll('.btn-valider-score');
            for (var k = 0; k < btnValiders.length; k++) {
                btnValiders[k].addEventListener('click', function() {
                    var matchId = this.getAttribute('data-matchid');
                    var equipe1 = this.getAttribute('data-equipe1');
                    var equipe2 = this.getAttribute('data-equipe2');
                    var poule = this.getAttribute('data-poule');
                    enregistrerScore(matchId, equipe1, equipe2, poule);
                });
            }
        }
        
        function toggleMatch(matchId) {
            var scoresDiv = document.getElementById('scores_' + matchId);
            var matchDiv = document.getElementById(matchId);
            var checkbox = matchDiv.querySelector('.match-checkbox');
            
            if (checkbox.checked) {
                scoresDiv.classList.remove('hidden');
                if (!matchsData[matchId]) {
                    matchsData[matchId] = { completed: true, score1: 0, score2: 0 };
                }
            } else {
                scoresDiv.classList.add('hidden');
                matchDiv.classList.remove('completed');
                if (matchsData[matchId]) {
                    delete matchsData[matchId];
                }
                calculerClassements();
            }
        }
        
        function enregistrerScore(matchId, equipe1, equipe2, poule) {
            var score1 = parseInt(document.getElementById('score1_' + matchId).value) || 0;
            var score2 = parseInt(document.getElementById('score2_' + matchId).value) || 0;
            
            matchsData[matchId] = {
                completed: true,
                score1: score1,
                score2: score2,
                equipe1: equipe1,
                equipe2: equipe2,
                poule: poule
            };
            
            document.getElementById(matchId).classList.add('completed');
            calculerClassements();
        }
        
        function calculerClassements() {
            var classements = {};
            
            for (var i = 0; i < config.poules.length; i++) {
                var poule = config.poules[i];
                classements[poule.nom] = {};
                
                for (var j = 0; j < poule.equipes.length; j++) {
                    var equipe = poule.equipes[j];
                    classements[poule.nom][equipe] = {
                        equipe: equipe,
                        joues: 0,
                        gagnes: 0,
                        perdus: 0,
                        points: 0,
                        marques: 0,
                        encaisses: 0,
                        diff: 0
                    };
                }
            }
            
            for (var matchId in matchsData) {
                var match = matchsData[matchId];
                if (match.completed) {
                    var stats1 = classements[match.poule][match.equipe1];
                    var stats2 = classements[match.poule][match.equipe2];
                    
                    stats1.joues++;
                    stats2.joues++;
                    stats1.marques += match.score1;
                    stats1.encaisses += match.score2;
                    stats2.marques += match.score2;
                    stats2.encaisses += match.score1;
                    
                    var ecart = Math.abs(match.score1 - match.score2);
                    
                    if (match.score1 > match.score2) {
                        stats1.gagnes++;
                        stats1.points += 4;
                        stats2.perdus++;
                        if (ecart <= 3) {
                            stats2.points += 1;
                        }
                    } else if (match.score2 > match.score1) {
                        stats2.gagnes++;
                        stats2.points += 4;
                        stats1.perdus++;
                        if (ecart <= 3) {
                            stats1.points += 1;
                        }
                    }
                    
                    stats1.diff = stats1.marques - stats1.encaisses;
                    stats2.diff = stats2.marques - stats2.encaisses;
                }
            }
            
            afficherClassements(classements);
        }
        
        function afficherClassements(classements) {
            var section = document.getElementById('classements-section');
            var container = document.getElementById('classementsContainer');
            
            var hasData = false;
            for (var poule in classements) {
                for (var equipe in classements[poule]) {
                    if (classements[poule][equipe].joues > 0) {
                        hasData = true;
                        break;
                    }
                }
            }
            
            if (!hasData) {
                section.classList.add('hidden');
                return;
            }
            
            section.classList.remove('hidden');
            var html = '';
            
            for (var poule in classements) {
                var equipes = [];
                for (var equipe in classements[poule]) {
                    equipes.push(classements[poule][equipe]);
                }
                
                equipes.sort(function(a, b) {
                    if (b.points !== a.points) return b.points - a.points;
                    if (b.diff !== a.diff) return b.diff - a.diff;
                    return b.marques - a.marques;
                });
                
                html += '<div class="classement-poule">';
                html += '<h3>Classement - ' + poule + '</h3>';
                html += '<table class="classement-table">';
                html += '<thead><tr>';
                html += '<th>Pos.</th><th>Équipe</th><th>J</th><th>G</th><th>P</th><th>Pts</th><th>PM</th><th>PE</th><th>Diff</th>';
                html += '</tr></thead><tbody>';
                
                for (var i = 0; i < equipes.length; i++) {
                    var eq = equipes[i];
                    if (eq.joues > 0) {
                        html += '<tr>';
                        html += '<td>' + (i + 1) + '</td>';
                        html += '<td><strong>' + eq.equipe + '</strong></td>';
                        html += '<td>' + eq.joues + '</td>';
                        html += '<td>' + eq.gagnes + '</td>';
                        html += '<td>' + eq.perdus + '</td>';
                        html += '<td><strong>' + eq.points + '</strong></td>';
                        html += '<td>' + eq.marques + '</td>';
                        html += '<td>' + eq.encaisses + '</td>';
                        html += '<td>' + (eq.diff >= 0 ? '+' : '') + eq.diff + '</td>';
                        html += '</tr>';
                    }
                }
                
                html += '</tbody></table></div>';
            }
            
            container.innerHTML = html;
        }
        
        function exportPDF() {
            var data = {
                poules: config.poules,
                nbTerrains: config.nbTerrains
            };
            
            fetch('/export_pdf', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            })
            .then(function(response) { return response.blob(); })
            .then(function(blob) {
                var url = window.URL.createObjectURL(blob);
                var a = document.createElement('a');
                a.href = url;
                a.download = 'tournoi_rugby.pdf';
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
            })
            .catch(function(error) { console.error('Erreur export:', error); });
        }
    </script>
</body>
</html>
'''

def generer_matchs_optimise(poules, nb_terrains):
    """
    Génère les matchs en optimisant les pauses entre matchs pour chaque équipe
    """
    tous_les_matchs = []
    toutes_les_equipes = set()
    
    for poule in poules:
        if len(poule['equipes']) < 2:
            continue
        equipes = poule['equipes']
        toutes_les_equipes.update(equipes)
        
        for equipe1, equipe2 in combinations(equipes, 2):
            tous_les_matchs.append({
                'equipe1': equipe1,
                'equipe2': equipe2,
                'poule': poule['nom']
            })
    
    if not tous_les_matchs:
        return {"terrains": [[] for _ in range(nb_terrains)], "planning": []}
    
    random.shuffle(tous_les_matchs)
    matchs_restants = tous_les_matchs.copy()
    dernier_tour = {e: -10 for e in toutes_les_equipes}
    tour = 0
    planning = []

    while matchs_restants:
        tour += 1
        matchs_tour = []
        equipes_occupees = set()
        matchs_scores = []
        
        for match in matchs_restants:
            e1, e2 = match['equipe1'], match['equipe2']
            score_pause = (tour - dernier_tour[e1]) + (tour - dernier_tour[e2])
            matchs_scores.append((score_pause, random.random(), match))
        
        matchs_scores.sort(reverse=True)
        
        for _, _, match in matchs_scores:
            e1, e2 = match['equipe1'], match['equipe2']
            if e1 not in equipes_occupees and e2 not in equipes_occupees:
                matchs_tour.append(match)
                equipes_occupees.update([e1, e2])
                dernier_tour[e1] = tour
                dernier_tour[e2] = tour
                matchs_restants.remove(match)
                if len(matchs_tour) == nb_terrains:
                    break
        
        while len(matchs_tour) < nb_terrains:
            matchs_tour.append(None)
        
        equipes_repos = [e for e in toutes_les_equipes if e not in equipes_occupees]
        planning.append({
            "tour": tour,
            "matches": matchs_tour,
            "repos": equipes_repos
        })
        
        if all(m is None for m in matchs_tour):
            break

    terrains = [[] for _ in range(nb_terrains)]
    for tour in planning:
        for i, match in enumerate(tour["matches"]):
            terrains[i].append(match)
    
    for terrain in terrains:
        while terrain and terrain[-1] is None:
            terrain.pop()
    
    return {"terrains": terrains, "planning": planning}


@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route('/generer_matchs', methods=['POST'])
def generer_matchs():
    data = request.json
    poules = data['poules']
    nb_terrains = data['nbTerrains']
    resultats = generer_matchs_optimise(poules, nb_terrains)
    return jsonify(resultats)


@app.route('/export_pdf', methods=['POST'])
def export_pdf():
    data = request.json
    poules = data['poules']
    nb_terrains = data['nbTerrains']
    
    resultats = generer_matchs_optimise(poules, nb_terrains)
    terrains = resultats["terrains"]
    planning = resultats["planning"]
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2d5016'),
        spaceAfter=30,
        alignment=1
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#4a7c2e'),
        spaceAfter=12
    )
    
    # Titre principal
    elements.append(Paragraph("🏉 Tournoi de Rugby - Planning des Matchs", title_style))
    elements.append(Spacer(1, 0.5*cm))
    
    # Informations sur les poules
    elements.append(Paragraph("Composition des poules", heading_style))
    for poule in poules:
        if poule['equipes']:
            elements.append(Paragraph(f"<b>{poule['nom']}</b>: {', '.join(poule['equipes'])}", styles['Normal']))
            elements.append(Spacer(1, 0.3*cm))
    elements.append(Spacer(1, 0.7*cm))
    
    # Planning global par tour
    elements.append(Paragraph("Planning des matchs (par tour)", heading_style))
    for tour in planning:
        elements.append(Spacer(1, 0.3*cm))
        elements.append(Paragraph(f"<b>Tour {tour['tour']}</b>", styles['Heading3']))
        
        table_data = [['Terrain', 'Équipe 1', 'vs', 'Équipe 2', 'Poule']]
        for i, match in enumerate(tour['matches'], start=1):
            if match is None:
                table_data.append([f"{i}", '-', '-', '-', 'Aucun match'])
            else:
                table_data.append([
                    f"{i}",
                    match['equipe1'],
                    'vs',
                    match['equipe2'],
                    match['poule']
                ])
        
        table = Table(table_data, colWidths=[2*cm, 5*cm, 1.5*cm, 5*cm, 4*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d5016')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#e8f5e9')])
        ]))
        elements.append(table)

        if tour['repos']:
            elements.append(Spacer(1, 0.2*cm))
            elements.append(Paragraph(f"Équipes au repos : <b>{', '.join(tour['repos'])}</b>", styles['Normal']))
        else:
            elements.append(Paragraph("Toutes les équipes jouent ce tour.", styles['Normal']))
        elements.append(Spacer(1, 0.5*cm))
    
    elements.append(Spacer(1, 1*cm))
    
    # Répartition par terrain
    elements.append(Paragraph("Organisation par terrain", heading_style))
    for terrain_idx, terrain in enumerate(terrains):
        elements.append(Spacer(1, 0.3*cm))
        elements.append(Paragraph(f"<b>Terrain {terrain_idx + 1}</b>", styles['Heading3']))
        
        table_data = [['Match', 'Équipe 1', 'vs', 'Équipe 2', 'Poule']]
        for match_idx, match in enumerate(terrain):
            if match is None:
                table_data.append([str(match_idx + 1), '-', '-', '-', 'Pas de match'])
            else:
                table_data.append([
                    str(match_idx + 1),
                    match['equipe1'],
                    'vs',
                    match['equipe2'],
                    match['poule']
                ])
        
        table = Table(table_data, colWidths=[2*cm, 5*cm, 1.5*cm, 5*cm, 4*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d5016')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#e8f5e9')])
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.5*cm))
    
    doc.build(elements)
    buffer.seek(0)
    
    return send_file(buffer, as_attachment=True, download_name='tournoi_rugby.pdf', mimetype='application/pdf')


if __name__ == '__main__':
    app.run(port=5001)