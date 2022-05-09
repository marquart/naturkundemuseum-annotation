<template>
    <div class="analysisTable">
        <h3 class="entityClick person" @click="emitDisplayTextOf(entityID)">{{entitiesMap[entityID].text}}</h3>
        <div
            v-for="(yearData,i) in actorLocationsTable[entityID]"
            :key="i"
            class="yearGrid"
        >
            <p class="year">{{yearData[0]}}:</p>
            <ul>
                <li
                    v-for="(lst,ii) in yearData[1]"
                    :key="ii"
                    class="entityClick place"
                    :style="{background: lst[2]}"
                    @click="emitDisplayTextOf(lst[0])"
                >
                    {{entitiesMap[lst[0]].text}} ({{lst[1]}}x)
                </li>
            </ul>
        </div>
    </div>

</template>

<script>


export default {
    name: 'AnalysisTable',
    props: {
        entitiesMap: Object,
        entityID: String,
        actorLocationsTable: Object
    },

    components : {
    },

    data() {
        return {

        }
    },

    watch: {
    },

    methods: {
        emitDisplayTextOf(id) {
            this.$emit("displayTextOf", id);
        },

    },



    mounted()  {
    },


}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
    .analysisTable {
        margin-left: 10%;
        margin-right: 10%;
        background: #FFF;

        padding: 1em;
        background: #ffffff;
        border: 1px solid #ffffff;
        border-radius: 2px;
        box-shadow: 6px 6px #CBCBCB;
    }

    .yearGrid {
        display: grid;
        gap: 3px;
        grid-template-columns: auto auto;
        align-items: center;
        justify-content: start;
    }

    .year {
        padding: 4px;
        margin: 2px;
        border: 2px solid #00000000;
    }

    .entityClick {
        display: inline-block;
        padding: 4px;
        margin: 2px;
        text-decoration: underline;
        background: #FFF;/*#EBEBEB;*/
        
    }

    .entityClick:hover {
        cursor: pointer;
        border: 3px solid #000000;        
    }

    .place {
        border: 3px solid #c7df7f;/*#fc7715aa;*/
        color: #000;
    }

    .person {
        border: 3px solid #00000000;
    }
</style>
