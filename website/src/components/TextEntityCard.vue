<template>
    <div class="card">
        <TextSnippet :texts="texts" :textidx="entity.txt_id" :lineidx="entity.line_idx" :pageline="entity.line"/>
        <div class="semanticData">
            <h2>Semantic Entity</h2>
            <h3 class="typeHeading">{{entity.text}}</h3>
            <h4 class="entityText cidocLink tooltip"><a :href="`https://cidoc-crm.org/html/cidoc_crm_v7.1.1.html#${entity.short_type}`" target="_blank"><p class="tooltiptext">{{cidocHoverText}}</p>{{entity.type}}</a></h4>
            <div class="itemLink tooltip" @click="emitDisplayGraphOf(entity.id)"><p class="tooltiptext">{{graphHoverText}}</p><img class="symbol" src="../assets/zoom.svg" alt="Graph Symbol"/> Show Neighborhood Graph</div>
            <div class="numericTable">
                <!--<div class="ncell">Source:</div>-->
                <div class="ncell">{{entity.citation ? entity.citation : '—'}}</div>

                <!--<div class="ncell"></div>-->
                <div v-show="entity.citation.length>0" class="ncell tooltip"><a :href="entity.url" target="_blank"><p class="tooltiptext">{{imageHoverText}}</p>{{entity.url}}</a></div>
                <!--
                <div class="ncell">Page:</div>
                <div class="ncell">{{entity.original_page &gt; 0 ? entity.original_page : '—'}}</div>

                <div class="ncell">Line:</div>
                <div class="ncell">{{entity.line &gt; -1 ? entity.line : '—'}}</div>

                <div class="ncell">Year:</div>
                <div class="ncell">{{entity.year &gt; 0 ? entity.year : '—'}}</div>

                <div class="ncell">Institution:</div>
                <div class="ncell">{{entity.institution}}</div>
                -->
            </div>

            <h4>Predecessors (incoming Relations)</h4>
            <div v-show="entity.incomingProps != undefined && entity.incomingProps.length > 0" class="propTable">
                <!--<div class="propItem tableHeading">Neighbor entity</div><div class="propItem"></div><div class="propItem tableHeading">CIDOC CRM Property</div><div class="propItem"></div>-->
                <template
                    v-for="(prop, i) in entity.incomingProps"
                    :key="i">
                    <!--<div class="propItem">{{prop.source.type}}:</div>-->
                    <div class="propItem itemLink tooltip" @click="showOneEntity(prop.source)"><p class="tooltiptext">{{neighborHoverText}}</p>{{prop.source.text}}</div>
                    <div class="propItem">🡺</div>
                    <div class="propItem cidocLink tooltip"><a :href="`https://cidoc-crm.org/html/cidoc_crm_v7.1.1.html#${prop.short_type}`" target="_blank"><p class="tooltiptext">{{cidocHoverText}}</p>{{prop.type}}</a></div>
                    <div class="propItem">🡺</div>
                </template>
            </div>
            <h4>Successors (outgoing Relations)</h4>
            <div v-show="entity.outgoingProps != undefined && entity.outgoingProps.length > 0" class="propTable">
                <!--<div class="propItem"></div><div class="propItem tableHeading">CIDOC CRM Property</div><div class="propItem"></div><div class="propItem tableHeading">Neighbor entity</div>-->
                <template
                    v-for="(prop, i) in entity.outgoingProps"
                    :key="i">
                    <div class="propItem">🡺</div>
                    <div class="propItem cidocLink tooltip"><a :href="`https://cidoc-crm.org/html/cidoc_crm_v7.1.1.html#${prop.short_type}`" target="_blank"><p class="tooltiptext">{{cidocHoverText}}</p>{{prop.type}}</a></div>
                    <div class="propItem">🡺</div>
                    <!--<div class="propItem">{{prop.target.type}}:</div>-->
                    <div class="propItem itemLink tooltip" @click="showOneEntity(prop.target)"><p class="tooltiptext">{{neighborHoverText}}</p>{{prop.target.text}}</div>
                </template>
            </div>
        </div>

    </div>

</template>

<script>
import TextSnippet from './TextSnippet.vue'

export default {
    name: 'TextEntityCard',
    components: {
        TextSnippet,
    },
    props: {
        entity: Object,
        texts: Object
    },
    data() {
        return {
            cidocHoverText: "Read definition in CIDOC documentation",
            graphHoverText: "Display the entity embedded in a visualization of our knowledge graph",
            neighborHoverText: "Jump to this entity",
            imageHoverText: "Go to digitized image of this page",
        }
    },

    emits: ['showOneEntity','displayGraphOf'],

    methods: {
        showOneEntity(item) {
            this.$emit('showOneEntity', item);
        },
        emitDisplayGraphOf(item_id) {
            this.$emit('displayGraphOf', item_id);
        },

    },
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
    .numericTable {
        display: grid;
        /*grid:
            'lcell rcell'
            'lcell rcell'
            'lcell rcell';*/
        /*grid-template-columns: 1fr 6fr; /*two columns*/
        grid-template-columns: auto; /*one column*/
        width: 80%;
        margin-left: 10%;
    }
    .semanticData {
        text-align: center;
    }

    .ncell {
        display: block;
        text-align: left;
        margin: 3px;
        border: 1px solid #f0f0f0;
        padding: 3px;
    }

    .card {
        display: grid;
        grid-template-columns: auto auto;
        background: #F6F6F6;
        width: 96%;
        margin-left: 2%;
        margin-bottom: 1.5em;
        /*border: 0.8ex solid #7da30b77;
        border: 1px solid #ffffff;
        border-radius: 2px;
        box-shadow: 6px 6px #CBCBCB;*/
    }


    .typeHeading {
        /*border-bottom: 0.5ex solid #EBEBEB;*/
        margin-bottom: 1ex;
    }

    .entityText {
        margin: 3px;
        padding: 0;
    }

    .propTable {
        display: grid;
        grid-template-columns: auto auto auto auto;
    }

    .propItem {
        border: 1px solid #f0f0f0;
    }

    .tableHeading {
        font-weight: 600;
        padding-bottom: 3px;
    }

    .itemLink {
        text-decoration: underline;
        background: #EBEBEB;
        border: 1px solid #00000000;
    }

    .itemLink:hover {
        cursor: pointer;
        border: 1px solid #000000;
    }

    .cidocLink {
        text-decoration: underline;
        color: black;
    }

    .cidocLink:hover {
        cursor: pointer;
    }

    .symbol {
        display: inline;
        height: 0.9em;
    }

    .tooltiptext {
        visibility: hidden;
        background-color: white;
        color: #000;
        text-align: center;
        padding: 3px;
        border-radius: 6px;
        font-weight: 100;
        display: block;
        margin-top: 2em;
        
        /* Position the tooltip text - see examples below! */
        position: absolute;
        z-index: 1;
    }

    .tooltip:hover .tooltiptext {
        visibility: visible;
    }

    @media screen and (max-width: 700px) {
        .card {
            grid-template-columns: auto;
        }
    
    }

</style>
