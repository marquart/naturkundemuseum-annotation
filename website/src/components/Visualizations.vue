<template>
    <div>
        <!--<p>Async fetching of individual graphs is not yet implemented, but it will look like this example:</p>-->
        <p>Through the interface below you can navigate the graph structure of our semantic web. Clicking the box of an entity displays the immediate neighborhood of that entity in the graph. You can jump to the location of the selected entity in the text by clicking the button "Show Entity in Text".</p>
        <p v-if="showerror" class="statusreport error">{{info}}</p>

        <div v-show="cursorId.length>0" class="navigationButton" @click="emitDisplayTextOf">🡸 Show Entity in Text</div>

        <inline-svg 
            id="graphviz"
            v-show="!showerror"
            :src="svg_src"
            @loaded="svgLoaded()"
            @unloaded="svgUnloaded()"
            @error="svgLoadError()"
        ></inline-svg>
        <p class="statusreport">{{info}}</p>
    </div>
</template>

<script>
import InlineSvg from 'vue-inline-svg';

export default {
  name: 'Visualizations',
  props: {
      entityId: String,
      baseBackend: String
  },

  components : {
      InlineSvg,
  },

  data() {
        return {
            backend: "",
            svg_src: "",
            showerror: false,
            info: "",
            listeners: [],
            cursorId: "",
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
                this.svg_src = this.buildSVGUrl(entityID);
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
        this.showerror = false;
        this.info = "SVG Loaded";
    },
    svgUnloaded() {
        this.info = "SVG Unloaded";
    },
    svgLoadError() {
        this.showerror = true;
        this.info = "ERROR: Unable to load SVG";
    },
    emitDisplayTextOf() {
        this.$emit("displayTextOf", this.cursorId);
    }
  },

  mounted()  {
    if (process.env.NODE_ENV == "production") {
        this.backend = this.baseBackend + "graphs/";
        this.svg_src = this.backend + "10420.svg";
        this.cursorId = '10420';
    } else {
        this.backend = this.baseBackend;
        this.svg_src = this.backend + "9774.svg";
        this.cursorId = '9774';


    }
  },


}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
    .graph {
        
    }

    #graphviz:deep(.semanticentity) {
        visibility: visible;
        pointer-events: visibleFill;
    }

    #graphviz:deep(.semanticentity:hover) {
        cursor: pointer;
    }

    #graphviz:deep(.semanticentity:hover polygon) {
        stroke: black;
        stroke-width: 3px;
    }

    .navigationButton {
        background: #FFFFFF;
        padding: 1ex;
        border: 1px solid #2c3e50;
        display: inline-block;
        float: left;

    }

    .navigationButton:hover {
        cursor: pointer;
        background: #EBEBEB;
    }

    .statusreport {
        font-style: italic;
    }

    .error {
        color: red;
    }
</style>
