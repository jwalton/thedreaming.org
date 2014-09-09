---
---
exports = window.thedreaming ?= {}

getLayer = (g, name, options={}) ->
    answer = g.select('g[data-layer-name="' + name + '"]')
    if answer.empty()
        answer = g.append('g').attr('data-layer-name', name)
        if options.class? then answer.attr('class', options.class)
        if options.transform? then answer.attr('transform', options.transform)

    if options.transform?
        d3.transition(answer)
            .attr('transform', options.transform)

    return answer

defineGettersSetters = (chart, gettersSetters) ->
    makeGetterSetter = (name) ->
        (value) ->
            if arguments.length is 0
                return chart.config[name]
            else
                chart.config[name] = value
                return chart

    chart.config ?= {}
    for name, defaultValue of gettersSetters
        chart.config[name] = defaultValue
        chart[name] = makeGetterSetter(name)

    return chart

# `data` should be an array of `{label, value}`.
#
exports.barGraph = ->
    chart = (selection) ->
        selection.each (data) ->
            g = d3.select(this)

            g.classed "barchart": true, "thedreamingchart": true

            margin = chart.config.margin
            width = chart.config.width
            height = chart.config.height
            content = {
                width: width - margin.left - margin.right,
                height: height - margin.top - margin.bottom
            }

            # Draw the xScale
            xScale = d3.scale.ordinal()
                .domain( data.map (d) -> d.label )
                .rangeRoundBands([0, content.width], 0.1)
            xAxis = d3.svg.axis()
                .scale(xScale)
                .orient("bottom")
            d3.transition(getLayer(g, "xAxis", {
                class: 'axis'
                transform: "translate(#{margin.left},#{margin.top + content.height})"
            })).call(xAxis)

            # Draw the yScale
            yScale = d3.scale.linear()
                .domain([0, d3.max(data, (d) -> d.value)])
                .range([content.height, 0])
            yAxis = d3.svg.axis()
                .scale(yScale)
                .orient("left")
            d3.transition(getLayer(g, "yAxis", {
                class: 'axis'
                transform: "translate(#{margin.left},#{margin.top})"
            })) .call(yAxis)

            # Draw the chart
            barEl = getLayer(g, "bars", {
                transform: "translate(#{margin.left},#{margin.top})"
            })

            bars = barEl.selectAll('rect')
                .data(data, (v) -> v.label)

            bars.enter()
                .append('rect')
                .attr({
                    height: 0
                    width: xScale.rangeBand()
                    x: (v) -> xScale(v.label)
                    y: content.height
                })
                .style({
                    opacity: 0
                    fill: chart.config.color
                })

            d3.transition(bars)
                .attr({
                    height: (v) -> content.height - yScale(v.value)
                    width: xScale.rangeBand()
                    x: (v) -> xScale(v.label)
                    y: (v) -> yScale(v.value)
                })
                .style({opacity: 1})

            d3.transition(bars.exit())
                .style({opacity: 0})

    defineGettersSetters chart, {
        width: 200,
        height: 200,
        color: '#AAF'
        margin:
            top: 10,
            left: 30,
            bottom: 30,
            right: 20
    }

    return chart
