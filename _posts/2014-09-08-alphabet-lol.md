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
        {letter: "R", date: "2014/09/19", win: true , gameId: "#", gameType: "TB"},
        {letter: "S", date: "2014/09/19", win: false , gameId: "1548311000", gameType: "TB"}


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
