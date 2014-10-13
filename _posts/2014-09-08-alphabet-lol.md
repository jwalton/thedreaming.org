---
title: Alphabet League of Legends Challenge
tags:
- LoL
date: '2014-09-08 23:00:00'
---
We've been playing a series of [League of Legends](http://na.leagueoflegends.com/) games where each game, every champion we pick must contain a given letter of the alphabet (so for the "A" game, every champion picked needs to have an "A" in the name, then for the next game every champion needs to have a "B", and so on.)

<!--more-->

Some letters are more difficult than others.  "B" for example, has only six champions to select from.  "P" has only five.  We've started using Team Builder so we can be sure we won't get banned. :smile:  "Q" will be impossible, an "Quinn" is the only champion available (unless Riot brings back One for All.)

This is a quick record of how we've been doing so far (will be updated as we go.)

<noscript>
    Javascript is required for visualizations.
</noscript>
<style>
    .lol-list {
        list-style-type: none;
        padding: 0;
        margin: 0;
    }

    .lol-list li {
        display: flex;
        align-items: center;
    }

    @media (min-width: 768px) {
        #lol-list {
            display: flex;
            justify-content: space-around;
        }
    }

    .lol-list .letter {
        flex: 0 0 30px;
        display: inline-block;
        font-size: 1.25em;
        width: 30px;
    }

    .lol-game {
        min-width: 150px;
        border-radius: 5px;
        display: inline-block;
        padding: 10px;
        margin: 2px 5px 3px 0px;
    }

    .lol-win, a.lol-win:visited, a.lol-win:hover, a.lol-win:link, a.lol-win:active {
        background-color: #015AAD;
        color: #f5d99e;
    }

    .lol-loss, a.lol-loss:visited, a.lol-loss:hover, a.lol-loss:link, a.lol-loss:active{
        background-color: #680006;
        color: #EEE;
    }

    .lol-game .status-icon {
        padding-right: 10px;
    }
    .lol-game .title {
        padding-right: 10px;
    }
    .lol-game .content {
    }

    .lol-game .lol-extras {
        font-size: .75em;
    }

    table {
        border-spacing: 2em 0;
        border-collapse: separate;
        margin-bottom: 2em;
        margin-left: -2em;
    }
    table th.name {
        text-align: left;
    }
    table td.name {
        text-align: left;
    }
    table td.number {
        text-align: right;
    }
</style>

<div id="lol-list">
</div>

<div style="width: 40%; min-width: 200px; margin: auto; text-align: center">
    <svg id="d3WinLossChart"></svg>
    ("Losses" does not include games that we lost, then replayed and won.)
</div>

### All games

<table><tr><th class="name">Name</th><th class="number">KDA</th><th class="number">KP%</th><th class="number">DPS</th><th class="number">HPS</th><th class="number">GPS</th><th class="number">KPM</th><th class="number">Wards/Game</th><th class="number">Deaths</th></tr><tr><td class="name">Allied Team</td><td class="number">2.01</td><td class="number">49.5</td><td class="number">49.11</td><td class="number">1.61</td><td class="number">5.22</td><td class="number">0.41</td><td class="number">48.5</td><td class="number">181</td></tr><tr><td class="name">Opposing Teams</td><td class="number">3.03</td><td class="number">47.1</td><td class="number">54.78</td><td class="number">1.69</td><td class="number">5.80</td><td class="number">0.48</td><td class="number">39.0</td><td class="number">142</td></tr><tr><td class="name">KatanaRabbit</td><td class="number">2.49</td><td class="number">51.1</td><td class="number">37.64</td><td class="number">0.44</td><td class="number">4.91</td><td class="number">0.40</td><td class="number">12.1</td><td class="number">144</td></tr><tr><td class="name">Teldon</td><td class="number">2.37</td><td class="number">58.0</td><td class="number">45.78</td><td class="number">2.08</td><td class="number">5.30</td><td class="number">0.44</td><td class="number">11.2</td><td class="number">160</td></tr><tr><td class="name">AmethystDream</td><td class="number">2.11</td><td class="number">42.7</td><td class="number">21.99</td><td class="number">1.76</td><td class="number">4.32</td><td class="number">0.34</td><td class="number">8.8</td><td class="number">142</td></tr><tr><td class="name">YumiWombat</td><td class="number">1.77</td><td class="number">57.8</td><td class="number">81.09</td><td class="number">3.40</td><td class="number">6.04</td><td class="number">0.46</td><td class="number">11.3</td><td class="number">229</td></tr><tr><td class="name">DigitalQuartz</td><td class="number">1.66</td><td class="number">52.1</td><td class="number">59.23</td><td class="number">0.41</td><td class="number">5.54</td><td class="number">0.41</td><td class="number">5.3</td><td class="number">221</td></tr></table>

### Games where we won

<table><tr><th class="name">Name</th><th class="number">KDA</th><th class="number">KP%</th><th class="number">DPS</th><th class="number">HPS</th><th class="number">GPS</th><th class="number">KPM</th><th class="number">Wards/Game</th><th class="number">Deaths</th></tr><tr><td class="name">Allied Team</td><td class="number">3.11</td><td class="number">49.7</td><td class="number">52.12</td><td class="number">2.17</td><td class="number">5.80</td><td class="number">0.49</td><td class="number">45.1</td><td class="number">52</td></tr><tr><td class="name">Opposing Teams</td><td class="number">1.85</td><td class="number">45.4</td><td class="number">50.24</td><td class="number">1.76</td><td class="number">5.10</td><td class="number">0.36</td><td class="number">25.5</td><td class="number">65</td></tr><tr><td class="name">KatanaRabbit</td><td class="number">4.28</td><td class="number">48.0</td><td class="number">44.40</td><td class="number">0.32</td><td class="number">5.44</td><td class="number">0.46</td><td class="number">11.3</td><td class="number">36</td></tr><tr><td class="name">AmethystDream</td><td class="number">4.09</td><td class="number">42.1</td><td class="number">16.54</td><td class="number">3.23</td><td class="number">4.64</td><td class="number">0.40</td><td class="number">9.6</td><td class="number">33</td></tr><tr><td class="name">Teldon</td><td class="number">3.92</td><td class="number">57.7</td><td class="number">48.83</td><td class="number">2.86</td><td class="number">5.88</td><td class="number">0.51</td><td class="number">9.1</td><td class="number">40</td></tr><tr><td class="name">YumiWombat</td><td class="number">2.67</td><td class="number">59.8</td><td class="number">89.82</td><td class="number">4.50</td><td class="number">6.97</td><td class="number">0.58</td><td class="number">11.1</td><td class="number">72</td></tr><tr><td class="name">DigitalQuartz</td><td class="number">2.25</td><td class="number">50.5</td><td class="number">61.73</td><td class="number">0.19</td><td class="number">6.14</td><td class="number">0.49</td><td class="number">4.4</td><td class="number">72</td></tr></table>

### Games where we lost

<table><tr><th class="name">Name</th><th class="number">KDA</th><th class="number">KP%</th><th class="number">DPS</th><th class="number">HPS</th><th class="number">GPS</th><th class="number">KPM</th><th class="number">Wards/Game</th><th class="number">Deaths</th></tr><tr><td class="name">Allied Team</td><td class="number">1.57</td><td class="number">49.4</td><td class="number">47.30</td><td class="number">1.27</td><td class="number">4.88</td><td class="number">0.36</td><td class="number">50.8</td><td class="number">129</td></tr><tr><td class="name">Opposing Teams</td><td class="number">4.01</td><td class="number">48.3</td><td class="number">57.51</td><td class="number">1.64</td><td class="number">6.22</td><td class="number">0.56</td><td class="number">48.2</td><td class="number">77</td></tr><tr><td class="name">KatanaRabbit</td><td class="number">1.90</td><td class="number">53.7</td><td class="number">33.57</td><td class="number">0.52</td><td class="number">4.59</td><td class="number">0.37</td><td class="number">12.6</td><td class="number">108</td></tr><tr><td class="name">Teldon</td><td class="number">1.85</td><td class="number">58.1</td><td class="number">44.10</td><td class="number">1.65</td><td class="number">4.99</td><td class="number">0.40</td><td class="number">12.5</td><td class="number">120</td></tr><tr><td class="name">AmethystDream</td><td class="number">1.51</td><td class="number">43.2</td><td class="number">25.26</td><td class="number">0.87</td><td class="number">4.13</td><td class="number">0.30</td><td class="number">8.3</td><td class="number">109</td></tr><tr><td class="name">DigitalQuartz</td><td class="number">1.37</td><td class="number">53.4</td><td class="number">57.72</td><td class="number">0.55</td><td class="number">5.18</td><td class="number">0.37</td><td class="number">5.9</td><td class="number">149</td></tr><tr><td class="name">YumiWombat</td><td class="number">1.36</td><td class="number">56.0</td><td class="number">75.83</td><td class="number">2.74</td><td class="number">5.49</td><td class="number">0.39</td><td class="number">11.5</td><td class="number">157</td></tr></table>

<script src="//cdnjs.cloudflare.com/ajax/libs/lodash.js/2.4.1/lodash.js"></script>
<script src="//cdnjs.cloudflare.com/ajax/libs/d3/3.4.11/d3.min.js"></script>
<script src="{{ site.baseurl }}/js/charts.js"></script>
<script>
(function() {
    var games = [
        {letter: "A", date: "2014/08/21", win: true,  gameId: "1503769380", gameType: "Draft"},
        {letter: "B", date: "2014/08/25", win: false, gameId: "1509033688", gameType: "Draft"},
        {letter: "C", date: "2014/08/25", win: true,  gameId: "1509102997", gameType: "Draft"},
        {letter: "D", date: "2014/08/27", win: false, gameId: "1511401723", gameType: "Draft"},
        {letter: "E", date: "2014/08/27", win: false, gameId: "1511452643", gameType: "Draft"},
        {letter: "E", date: "2014/08/29", win: true,  gameId: "1514152049", gameType: "Draft", notes: "Missing usual player"},
        {letter: "F", date: "2014/08/30", win: true,  gameId: "1515279338", gameType: "Draft", notes: "With disconnects"},
        {letter: "G", date: "2014/09/02", win: false, gameId: "1521284882", gameType: "Draft"},
        {letter: "H", date: "2014/09/04", win: false, gameId: "1525473140", gameType: "Blind"},
        {letter: "I", date: "2014/09/04", win: true,  gameId: "1525539867", gameType: "Draft"},
        {letter: "J", date: "2014/09/05", win: false, gameId: "1527669642", gameType: "Draft"},
        {letter: "K", date: "2014/09/07", win: true,  gameId: "1531851183", gameType: "TB"},
        {letter: "L", date: "2014/09/08", win: false, gameId: "1533122741", gameType: "TB"},
        {letter: "M", date: "2014/09/08", win: false, gameId: "1533202510", gameType: "TB"},
        {letter: "N", date: "2014/09/09", win: true,  gameId: "1534354027", gameType: "TB"},
        {letter: "O", date: "2014/09/09", win: true,  gameId: "1534324677", gameType: "TB"},
        {letter: "P", date: "2014/09/13", win: false, gameId: "1539614301", gameType: "TB"},
        {letter: "Q", date: "2014/09/19", win: false, gameId: "1548309979", gameType: "TB"},
        {letter: "R", date: "2014/09/19", win: true , gameId: "1548370013", gameType: "TB"},
        {letter: "S", date: "2014/09/19", win: false, gameId: "1548311000", gameType: "TB"},
        {letter: "T", date: "2014/10/02", win: true,  gameId: "1566342202", gameType: "TB"},
        {letter: "U", date: "2014/10/02", win: false, gameId: "1566342981", gameType: "TB"},
        {letter: "V", date: "2014/10/05", win: false, gameId: "1570513554", gameType: "TB"},
        {letter: "W", date: "2014/10/05", win: false, gameId: "1570514223", gameType: "TB"},
        {letter: "X", date: "2014/10/09", win: false, gameId: "1575395894", gameType: "TB"},
        {letter: "Y", date: "2014/10/10", win: true,  gameId: "1576478189", gameType: "TB"},
        {letter: "Z", date: "2014/10/10", win: false, gameId: "1576478918", gameType: "TB"}
    ];
    var getMatchHistoryUrl = function(game) {
        return "http://matchhistory.na.leagueoflegends.com/en/#match-details/NA1/" + game.gameId;
    };

    // Draw a box for a game.
    var renderGame = function(game) {
        var gameClass = game.win ? "lol-win" : "lol-loss";
        var gameIcon = game.win ? "fa-check-circle" : "fa-times-circle";
        var title = game.win ? "Victory" : "Defeat";
        var extras = [game.date,  game.gameType];
        if(game.notes != null) {extras.push(game.notes);}

        return '<a href="' + getMatchHistoryUrl(game) + '" class="lol-game ' + gameClass + '">' +
            '<span class="status-icon"><i class="fa ' + gameIcon + '"></i></span>' +
            '<span class="content"><span class="title">' + title + '</span>' +
            '<span class="lol-extras">' + extras.join(" • ") + '</span></span></a>'
    }

    // Build the table of games by letter.
    var i = 0;
    var gamesByLetter = _(games)
        .groupBy('letter')
        .map(function(gamesForLetter) {
            return _.extend(gamesForLetter, {letterIndex: i++});
        })
        .value();

    var lolListEl = d3.select('#lol-list');

    // Render the list of games for a given letter.
    var makeGameListForLetter = function(games) {
        var g = d3.select(this);
        g.append('span')
            .classed({letter: true})
            .text( games[0].letter );
        wrapper = g.append('span')
        wrapper.selectAll('span')
            .data(games)
            .enter()
            .append('span')
            .each( function(v) {
                var g = d3.select(this);
                g.html(renderGame(v));
            });
    }

    var drawGamesTable = function (gamesByLetter) {
        var containerEl = lolListEl.append('ul').classed({'lol-list': true});

        containerEl.selectAll('li')
            .data(gamesByLetter, function(games) {return games[0].letter;})
            .enter()
            .append('li')
            .style({opacity: 0})
            .each(makeGameListForLetter)
            .transition()
            .delay(function(v,i) {
                return v.letterIndex * 50;
            })
            .duration(1000)
            .style({opacity:1})
            .attr({'class': true});
    }

    mid = Math.ceil(gamesByLetter.length/2);
    firstHalf = gamesByLetter.slice(0,mid);
    lastHalf = gamesByLetter.slice(mid,gamesByLetter.length);
    drawGamesTable(firstHalf);
    drawGamesTable(lastHalf);

    // Build the graph of wins and losses
    wins = _.reduce(games, function(sum, game) {return sum + (game.win ? 1 : 0);}, 0);
    losses = _(games)
        .groupBy('letter')
        // Turn each group of games into a true if they are all losses, false otherwise.
        .map(function(gamesForLetter) {
            return _.all(gamesForLetter, function(g) {
                return !g.win;
            });
        })
        .reduce(function(sum, v) {
            return sum + (v ? 1 : 0);
        }, 0);
    totalLosses = games.length - wins;

    var data = [
        {label: "Wins", value: wins},
        {label: "Losses", value: losses},
        {label: "Total Losses", value: totalLosses}
    ];

    function drawChart(duration) {
        duration |= 0;

        var parent = document.getElementById('d3WinLossChart').parentElement;
        var width = parent.clientWidth;
        var height = 200;
        var svg = d3.select("#d3WinLossChart")
            .datum(data)

        var chart = thedreaming.barGraph();
        chart.width(width);
        chart.height(height);
        svg
            .transition()
            .duration(duration)
            .attr({
                width: width,
                height: height
            })
            .call(chart);
    }

    drawChart(1000);
    window.addEventListener('resize', drawChart);

})();
</script>
