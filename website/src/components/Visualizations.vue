<template>
    <div>
        <p>Async fetching of individual graphs is not yet implemented, but it will look like this example:</p>
        <p>{{info}}</p>
        <inline-svg 
            id="graphviz"
            v-show="!showerror"
            :src="svg_src"
            @loaded="svgLoaded()"
            @unloaded="svgUnloaded()"
            @error="svgLoadError()"
        ></inline-svg>
    </div>
</template>

<script>
import InlineSvg from 'vue-inline-svg';
import TempSVGLocations from '../data/Temp_SVG_Lookup.json';

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
            backend: "https://aron-marquart.de/mfn-chronik/graphs/",
            svg_src: "https://aron-marquart.de/mfn-chronik/graphs/10420.svg",
            showerror: false,
            info: "",
            listeners: [],
            cursorId: '',

            // only temporary:
            temp_fetching: true,
            temp_cursor: 0,
            temp_svg_locations: TempSVGLocations,

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
            this.requestSVG(this.entityId);
        }
  },

  methods: {
    requestSVG(entityID) {
        if (process.env.NODE_ENV == "production") {
            if (entityID.length > 0 && entityID !== this.cursorId) {
                this.removeListeners();
                this.cursorId = entityID;
                if (this.temp_fetching) this.svg_src = this.next_temp_svg();
                else this.svg_src = this.buildSVGUrl(entityID);
            }
        }
    },
    requestSVGinternal(event) {
        event.stopPropagation();
        let targetID = event.currentTarget.id;
        if (targetID.startsWith('N')) this.requestSVG(targetID.slice(1));
    },
    buildSVGUrl(entityId) {
        return this.backend + entityId + ".svg"
    },
    makeNodesClickable() {
        let svg = document.getElementById('graphviz')
        this.listeners = [...svg.getElementsByClassName('semanticentity')];
        this.listeners.forEach((e) => {
            e.addEventListener("click", this.requestSVGinternal, false);
        });
    },
    removeListeners(){
        this.listeners.forEach((e) => {
            e.removeEventListener('click', this.requestSVGinternal, false);
        });
    },
    svgLoaded() {
        this.makeNodesClickable();
        this.info = "SVG Loaded";
    },
    svgUnloaded() {
        this.info = "SVG Unloaded";
    },
    svgLoadError() {
        this.showerror = true;
        this.info = "Unable to load SVG";
    },
    next_temp_svg() {
        this.temp_cursor += 1;
        if (this.temp_cursor > this.temp_svg_locations.length-1) this.temp_cursor = 0;
        return this.temp_svg_locations[this.temp_cursor];

    }
  },

}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style>
    .graph {
        
    }

    g.semanticentity {
        visibility: visible;
        pointer-events: visible;
    }

    g.semanticentity:hover {
        cursor: pointer;
    }
</style>
