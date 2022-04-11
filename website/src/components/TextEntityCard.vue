<template>
    <div class="card">
        <TextSnippet :texts="texts" :textidx="entity.txt_id" :lineidx="entity.line_idx" :pageline="entity.line"/>
        <div class="semanticData">
            <h2 class="typeHeading">{{entity.text}}</h2>
            <h3 class="entityText">{{entity.type}}</h3>
            <p class="itemLink" @click="emitDisplayGraphOf(entity.id)"><img class="symbol" src="../assets/zoom.svg" alt="Graph Symbol"/> Show Neighborhood Graph</p>
            <div class="numericTable">
                <div class="lcell">ID:</div>
                <div class="rcell">{{entity.id}}</div>

                <div class="lcell">Page:</div>
                <div class="rcell">{{entity.page}}</div>

                <div class="lcell">Line:</div>
                <div class="rcell">{{entity.line}}</div>

                <div class="lcell">Year:</div>
                <div class="rcell">{{entity.year}}</div>

                <div class="lcell">Institution:</div>
                <div class="rcell">{{entity.institution}}</div>
            </div>

            <h4>Predecessors (incoming Relations)</h4>
            <div class="propTable">
                <template
                    v-for="(prop, i) in entity.incomingProps"
                    :key="i">
                    <div class="propItem">{{prop.source.type}}:</div>
                    <div class="propItem itemLink" @click="showOneEntity(prop.source)">{{prop.source.text}}</div>
                    <div class="propItem">🡺</div>
                    <div class="propItem">{{prop.type}}</div>
                    <div class="propItem">🡺</div>
                </template>
            </div>
            <h4>Successors (outgoing Relations)</h4>
            <div class="propTable">
                <template
                    v-for="(prop, i) in entity.outgoingProps"
                    :key="i">
                    <div class="propItem">🡺</div>
                    <div class="propItem">{{prop.type}}</div>
                    <div class="propItem">🡺</div>
                    <div class="propItem">{{prop.target.type}}:</div>
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
        grid-template-columns: 1fr 6fr;
        width: 60%;
        margin-left: 20%;
    }
    .semanticData {
        text-align: center;
        
    }

    .lcell {
        /*grid-area: 'lcell';*/
        display: block;
        text-align: left;
        margin: 3px;
        border: 1px solid #f0f0f0;
        padding: 3px;
    }

    .rcell {
        /*grid-area: 'rcell';*/
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
        width: 90%;
        margin-left: 5%;
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
        grid-template-columns: auto auto auto auto auto;
    }

    .propItem {
        border: 1px solid #f0f0f0;
    }

    .itemLink {
        text-decoration: underline;
    }

    .itemLink:hover {
        cursor: pointer;
        background: #EBEBEB;
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
