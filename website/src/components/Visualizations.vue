<template>
    <div>
        <p>Async fetching of individual graphs is not yet implemented, but it will look like this example:</p>
        <inline-svg 
            :src="require('../assets/11732.svg')"
            :transformSource="makeNodesClickable"

        ></inline-svg>

        <!--
                        transformSource="transformSvg"
            @loaded="svgLoaded($event)"
            @unloaded="svgUnloaded()"
            @error="svgLoadError($event)"
        <a href="../assets/11536.svg" target="_blank">
            <img class="graph"
                src="../assets/11536.svg"
                alt="Neighborhood graph for Entity 11536"
            />
        </a>
        -->
    </div>
</template>

<script>
import InlineSvg from 'vue-inline-svg';

export default {
  name: 'Visualizations',
  props: {
      entityId: String
  },

  components : {
      InlineSvg,
  },

  data() {
    return {
        svg_src: "../assets/11536.svg"
    }
  },

  methods: {
    makeNodesClickable(svg) {
        let entities = svg.getElementsByClassName('entities');
        console.log(entities);

        for (let element of entities) {
            element.setAttribute('pointer-events','bounding-box');
            element.setAttribute('click',this.requestSVG);
        }


        return svg;
    },
    requestSVG(event) {
        console.log(event.target);
    }
  },

}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
    .graph {
        
    }

    g.entities {
        pointer-events: all;
    }

    g.entities:hover {
        cursor: pointer;
    }
</style>
