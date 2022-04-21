<template>
    <div class="card">
        <TextSnippet :texts="texts" :textidx="entity.txt_id" :lineidx="entity.line_idx" :pageline="entity.line"/>
        <div class="semanticData">
            <h2>Semantic Entity</h2>
            <h3 class="typeHeading">{{entity.text}}</h3>
            <h4 class="entityText cidocLink"><a :href="`https://cidoc-crm.org/html/cidoc_crm_v7.1.1.html#${entity.short_type}`" target="_blank">{{entity.type}}</a></h4>
            <p class="itemLink" @click="emitDisplayGraphOf(entity.id)"><img class="symbol" src="../assets/zoom.svg" alt="Graph Symbol"/> Show Neighborhood Graph</p>
            <div class="numericTable">
                <!--<div class="ncell">Source:</div>-->
                <div class="ncell">{{entity.citation ? entity.citation : '—'}}</div>

                <!--<div class="ncell"></div>-->
                <div class="ncell"><a :href="entity.url" target="_blank">{{entity.url}}</a></div>
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
            <div class="propTable">
                <template
                    v-for="(prop, i) in entity.incomingProps"
                    :key="i">
                    <!--<div class="propItem">{{prop.source.type}}:</div>-->
                    <div class="propItem itemLink" @click="showOneEntity(prop.source)">{{prop.source.text}}</div>
                    <div class="propItem">🡺</div>
                    <div class="propItem cidocLink"><a :href="`https://cidoc-crm.org/html/cidoc_crm_v7.1.1.html#${prop.short_type}`" target="_blank">{{prop.type}}</a></div>
                    <div class="propItem">🡺</div>
                </template>
            </div>
            <h4>Successors (outgoing Relations)</h4>
            <div class="propTable">
                <template
                    v-for="(prop, i) in entity.outgoingProps"
                    :key="i">
                    <div class="propItem">🡺</div>
                    <div class="propItem cidocLink"><a :href="`https://cidoc-crm.org/html/cidoc_crm_v7.1.1.html#${prop.short_type}`" target="_blank">{{prop.type}}</a></div>
                    <div class="propItem">🡺</div>
                    <!--<div class="propItem">{{prop.target.type}}:</div>-->
                    <div class="propItem itemLink" @click="showOneEntity(prop.target)">{{prop.target.text}}</div>
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

    .itemLink {
        text-decoration: underline;
        background: #EBEBEB;
    }

    .itemLink:hover {
        cursor: pointer;
        border: 1px solid black;
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

    @media screen and (max-width: 700px) {
        .card {
            grid-template-columns: auto;
        }
    
    }

</style>
