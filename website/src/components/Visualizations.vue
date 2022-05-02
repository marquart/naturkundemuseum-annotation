<template>
    <div>
        <!--<p>Async fetching of individual graphs is not yet implemented, but it will look like this example:</p>-->
        <p>Through the interface below you can navigate the graph structure of our semantic web. Clicking the box of an entity displays the immediate neighborhood of that entity in the graph. You can jump to the location of the selected entity in the text by clicking the button "<img class="symbol" src="../assets/book.svg" alt="Book Symbol"/> Show Entity in Text". If you want to start exploring the graph from a random node, click on the "<img class="symbol" src="../assets/dice-solid.svg" alt="Dice Symbol"/> Start with random Entity" button.</p>
        <div v-show="showerror" class="errormsg"><strong>{{info}}</strong></div>

        <div class="navigationElements">
            <div v-show="cursorId.length>0" class="navigationButton functionalButton" @click="emitDisplayTextOf"><img class="symbol" src="../assets/book.svg" alt="Book Symbol"/> Show Entity in Text</div>
            <div class="navigationButton functionalButton" @click="getRandomEntityID"><img class="symbol" src="../assets/dice-solid.svg" alt="Dice Symbol"/> Start with random Entity</div>
        </div>

        <div class="navigationElements">
            <div v-if="historyCursor>0" class="navigationButton buttonLeft" @click="navigateHistory(-1)">🡸 Go Back</div> <!---->
            <div v-if="historyCursor<history.length-1" class="navigationButton buttonRight" @click="navigateHistory(1)" >Go Forward 🡺</div><!---->
        </div>

        <inline-svg 
            id="graphviz"
            ref="graphviz"
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

            history: [],
            historyCursor: -1,
        }

  },

  watch: {
        entityId() {
            this.requestSVG(this.entityId, true);
        }
  },

  methods: {
    // REQUESTS
    requestSVG(entityID, historyPush) {
        if (process.env.NODE_ENV == "production") {
            if (entityID != undefined && entityID.length > 0 && entityID !== this.cursorId) {
                this.removeListeners();
                this.cursorId = entityID;
                if (historyPush) this.pushHistory();
                this.svg_src = this.buildSVGUrl(entityID);
            }
        }
    },
    requestSVGinternal(event) {
        event.stopPropagation();
        const targetID = event.currentTarget.id;
        if (targetID.startsWith('N')) this.requestSVG(targetID.slice(1), true);
        else if (targetID.startsWith('V_')) this.requestSVG(targetID.slice(2), true);
    },
    buildSVGUrl(entityId) {
        return this.backend + entityId + ".svg"
    },

    // SVG EVENTS
    makeNodesClickable() {
        this.listeners = [...this.$refs.graphviz.$el.getElementsByClassName('entityNode')];
        this.listeners.forEach((e) => {
            e.addEventListener("click", this.requestSVGinternal, false);
        });
    },
    removeListeners(){
        this.listeners.forEach((e) => {
            e.removeEventListener('click', this.requestSVGinternal, false);
        });
    },
    emitDisplayTextOf() {
        this.$emit("displayTextOf", this.cursorId);
    },

    // HISTORY
    pushHistory() {
        if (this.cursorId.length > 0) {
            if (this.historyCursor !== this.history.length-1) {
                let delta = this.history.length-this.historyCursor-1;
                this.history.splice(this.historyCursor+1, delta);
            }
            if (this.history.length > 15) this.history.shift();
            this.history.push(this.cursorId);
            this.historyCursor = this.history.length-1;
        }
    },

    navigateHistory(delta) {
        this.historyCursor = this.historyCursor + delta;
        if (0 <= this.historyCursor && this.historyCursor < this.history.length) {
            this.requestSVG(this.history[this.historyCursor], false);
        } else {
            this.historyCursor =  this.historyCursor - delta;
        }
    },


    // SVG STATES
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
        this.info = "ERROR: Unable to load SVG!";
    },

    // random int
    getRandomEntityID() {
        this.$emit("randomEntity");
    },

  },

  mounted()  {
    if (process.env.NODE_ENV == "production") {
        this.backend = this.baseBackend + "graphs/";
        this.requestSVG(this.getRandomEntityID(), true);
    } else {
        this.backend = this.baseBackend;
        this.cursorId = '9774';
        this.svg_src = this.backend + "9774.svg";
        //console.log(this.svg_src);
    }
  },


}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
    #graphviz:deep(.entityNode) {
        visibility: visible;
        pointer-events: visibleFill;
    }

    #graphviz:deep(.entityNode:hover) {
        cursor: pointer;
    }

    #graphviz:deep(.entityNode:hover polygon) {
        stroke: black;
        stroke-width: 3px;
    }

    .navigationElements {
        display: block;
        width: 90%;
        margin-left: 5%;
        text-align: center;
    }
    
    .functionalButton {
        margin: 1ex;
        align: center;
    }

    .buttonRight {
        float: right;
    }

    .buttonLeft {
        float: left;
    }

    .navigationButton {
        background: #FFFFFF;
        padding: 1ex;
        border: 1px solid #2c3e50;
        display: inline-block;
        /*float: left;*/
    }

    .navigationButton:hover {
        cursor: pointer;
        background: #EBEBEB;
    }

    .statusreport {
        font-style: italic;
    }

    .symbol {
        display: inline;
        height: 0.9em;
    }
</style>
