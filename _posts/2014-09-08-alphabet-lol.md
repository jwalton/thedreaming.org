---
title: Alphabet League of Legends Challenge
tags:
- LoL
date: '2014-09-08 23:00:00'
---
We've been playing a series of [League of Legends](http://na.leagueoflegends.com/) games where each game, every champion we pick must contain a given letter of the alphabet (so for the "A" game, every champion picked needs to have an "A" in the name, then for the next game every champion needs to have a "B", and so on.)

<!--more-->

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

@media (min-width: 768px) {
    #lol-list {
        display: flex;
        justify-content: space-around;
    }
}

.lol-list li {
    -webkit-transition: opacity 1s ease-in-out;
    -moz-transition: opacity 1s ease-in-out;
    -ms-transition: opacity 1s ease-in-out;
    -o-transition: opacity 1s ease-in-out;
    transition: opacity 1s ease-in-out;
    opacity: 1;
    padding-bottom: 0.25em;
}

.lol-list li.invisible {
    opacity: 0;
}

.lol-list .letter {
    display: inline-block;
    font-size: 2em;
    width: 30px;
}

.lol-game {
    min-width: 100px;
    border-radius: 5px;
    display: inline-block;
    padding: 10px;
    margin-right: 5px;
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
    font-size: 2em;
    padding-right: 10px;
}
.lol-game .content {
    float: right;
}

.lol-game .lol-extras {
    font-size: .75em;
}
</style>

<div id="lol-list">
</div>

<div style="width: 40%; min-width: 200px; margin: auto; text-align: center">
    <svg id="d3WinLossChart"></svg>
    ("Losses" does not include games that we lost, then replayed and won.)
</div>

<script src="//cdnjs.cloudflare.com/ajax/libs/lodash.js/2.4.1/lodash.js"></script>
<script src="//cdnjs.cloudflare.com/ajax/libs/d3/3.4.11/d3.min.js"></script>
<script src="{{ site.baseurl }}/js/charts.js"></script>
<script>
(function() {
    var games = [
        {letter: "A", date: "2014/08/21", win: true,  gameId: "1503769380"},
        {letter: "B", date: "2014/08/25", win: false, gameId: "1509033688"},
        {letter: "C", date: "2014/08/25", win: true,  gameId: "1509102997"},
        {letter: "D", date: "2014/08/27", win: false, gameId: "1511401723"},
        {letter: "E", date: "2014/08/27", win: false, gameId: "1511452643"},
        {letter: "E", date: "2014/08/29", win: true,  gameId: "1514152049", notes: "With Dream Godling"},
        {letter: "F", date: "2014/08/29", win: true,  gameId: "1521284882", notes: "With disconnects"},
        {letter: "G", date: "2014/09/02", win: false, gameId: "1521284882"},
        {letter: "H", date: "2014/09/04", win: false, gameId: "1525473140"},
        {letter: "I", date: "2014/09/04", win: true,  gameId: "1525539867"},
        {letter: "J", date: "2014/09/05", win: false, gameId: "1527669642"},
        {letter: "K", date: "2014/09/07", win: true,  gameId: "1531851183"},
        {letter: "L", date: "2014/09/08", win: false, gameId: "1533122741"},
        {letter: "M", date: "2014/09/08", win: false, gameId: "1533202510"},
        {letter: "N", date: "2014/09/09", win: true,  gameId: "1534354027"},
        {letter: "O", date: "2014/09/09", win: true,  gameId: "1534324677"},

    ];
    var getMatchHistoryUrl = function(game) {
        return "http://matchhistory.na.leagueoflegends.com/en/#match-details/NA1/" + game.gameId;
    };

    // Build the table of games by letter.
    var gamesByLetter = _(games).groupBy('letter').toArray().value();

    var lolListEl = d3.select('#lol-list');

    var makeGameListForLetter = function(games) {
        var g = d3.select(this);
        g.append('td')
            .classed({letter: true})
            .text( games[0].letter );
        wrapper = g.append('td')
        wrapper.selectAll('a.lol-game')
            .data(games)
            .enter()
            .append('a')
            .attr({
                href: getMatchHistoryUrl
            })
            .classed({
                "lol-game": true,
                "lol-win": function(v) {return v.win;},
                "lol-loss": function(v) {return !v.win;}
            })
            .each( function(v) {
                var g = d3.select(this);
                content = g.append('span').classed({content: true});
                content.append('div').text(v.win ? 'Victory' : 'Defeat');
                content.append('div')
                    .classed({"lol-extras": true})
                    .text(v.date + (v.notes ? " • " + v.notes : ""));
                g.append('span')
                    .classed({"status-icon": true})
                    .html(v.win?"<i class='fa fa-check-circle'></i>":"<i class='fa fa-times-circle'></i>")
            });
    }

    var drawGamesTable = function (gamesByLetter) {
        var containerEl = lolListEl.append('table').classed({'lol-list': true});

        containerEl.selectAll('tr')
            .data(gamesByLetter, function(games) {return games[0].letter;})
            .enter()
            .append('tr')
            .classed({invisible: true})
            .each(makeGameListForLetter)
            .transition()
            .delay(function(v,i) {return i * 100;})
            .attr({'class': true});
    }

    mid = Math.floor(gamesByLetter.length/2);
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