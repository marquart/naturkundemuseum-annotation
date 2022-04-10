<template>
    <div>
        <p>Async fetching of individual graphs is not yet implemented, but it will look like this example:</p>
        <p>{{info}}</p>
        <inline-svg 
            v-if="!showerror"
            :src="svg_src"
            @loaded="svgLoaded()"
            @unloaded="svgUnloaded()"
            @error="svgLoadError()"
        ></inline-svg>

        <!--
            :transformSource="makeNodesClickable"

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
//import InlineSvg from './InlineSVG.vue'

export default {
  name: 'Visualizations',
  props: {
      entityId: String
  },

  components : {
      InlineSvg,
  },

  data() {
    if (process.env.NODE_ENV == "production") {
        return {
            svg_src: "https://aron-marquart.de/mfn-chronik/graphs/12647.svg",
            showerror: false,
            info: ""
        }
    } else {
        return {
            svg_src: require("../assets/12647.svg"),
            showerror: false,
            info: ""
        }
    }
  },

  watch: {
        entityId() {
            if (process.env.NODE_ENV == "production") {
                if (this.entityId.length > 0) this.svg_src = "https://aron-marquart.de/mfn-chronik/graphs/" + this.entityId + ".svg";
            }
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
    },
    svgLoaded() {
        this.info = "SVG Loaded"; 
    },
    svgUnloaded() {
        this.info = "SVG UnLoaded";
    },
    svgLoadError() {
        this.showerror = true;
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
