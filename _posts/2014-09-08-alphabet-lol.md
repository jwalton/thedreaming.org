---
title: Alphabet League of Legends Challenge
tags:
- LoL
date: '2014-09-08 23:00:00'
---
We've been playing a series of [League of Legends](http://na.leagueoflegends.com/) games where each game, every champion we pick must contain a given letter of the alphabet (so for the "A" game, every champion picked needs to have an "A" in the name, then for the next game every champion needs to have a "B", and so on.)

<!--more-->

This is a quick record of how we've been doing so far (will be updated as we go.)

* A - [08/21 - Win](http://matchhistory.na.leagueoflegends.com/en/#match-details/NA1/1503769380)
* B - [08/25 - Loss](http://matchhistory.na.leagueoflegends.com/en/#match-details/NA1/1509033688)
* C - [08/25 - Win](http://matchhistory.na.leagueoflegends.com/en/#match-details/NA1/1509102997)
* D - [08/27 - Loss](http://matchhistory.na.leagueoflegends.com/en/#match-details/NA1/1511401723)
* E
  * [08/27 - Loss](http://matchhistory.na.leagueoflegends.com/en/#match-details/NA1/1511452643),
  * [08/29 - Win with Dream Godling](http://matchhistory.na.leagueoflegends.com/en/#match-details/NA1/1514152049)
* F - [09/02 - Win (with disconnects)](http://matchhistory.na.leagueoflegends.com/en/#match-details/NA1/1521284882)
* G - [09/02 - Loss](http://matchhistory.na.leagueoflegends.com/en/#match-details/NA1/1521284882)
* H - [09/04 - Loss](http://matchhistory.na.leagueoflegends.com/en/#match-details/NA1/1525473140)
* I - [09/04 - Win](http://matchhistory.na.leagueoflegends.com/en/#match-details/NA1/1525539867)
* J - [09/05 - Loss](http://matchhistory.na.leagueoflegends.com/en/#match-details/NA1/1527669642)
* K - [09/07 - Win](http://matchhistory.na.leagueoflegends.com/en/#match-details/NA1/1531851183)
* L - [09/08 - Loss](http://matchhistory.na.leagueoflegends.com/en/#match-details/NA1/1533122741)
* M - [09/08 - Loss](http://matchhistory.na.leagueoflegends.com/en/#match-details/NA1/1533202510)

<div style="width: 40%; min-width: 200px; margin: auto; text-align: center">
    <svg id="d3WinLossChart"></svg>
    ("Losses" does not include games that we lost, then replayed and won.)
</div>
<script src="//cdnjs.cloudflare.com/ajax/libs/d3/3.4.11/d3.min.js"></script>
<script src="{{ site.baseurl }}/js/charts.js"></script>
<script>
(function() {
    var data = [
        {label: "Wins", value: 6},
        {label: "Losses", value: 7},
        {label: "Total Losses", value: 8}
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