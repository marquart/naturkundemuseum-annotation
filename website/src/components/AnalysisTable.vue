<template>
    <div class="analysisTable">
        <h3 class="entityClick person">{{displayEntity[1]}}</h3>
        <p>{{displayEntity[2].toString()}}</p>
        <!--<div
            class="yearGrid"
        >-->
        <table>
            <tr
                v-for="(yearData,i) in entityData[0]"
                :key="i"
                class="row"
            >
                <!--Column1: Year-->
                <th class="item year">{{years[i]}}:</th>
                <!--Column2:-->
                <td><ul class="item">
                    <li
                        v-for="(lst,ii) in yearData"
                        :key="ii"
                        class="entityClick place"
                        :style="{'color': lst[2], 'font-size': lst[1] + 'px'}"
                        @click="emitDisplayTextOf(lst[0])"
                    >
                        {{entitiesMap[lst[0]].text}}
                        <!--{{entitiesMap[lst[0]].text}} ({{lst[1]}}x)-->
                    </li>
                </ul></td>
                <!--Column3:-->
                <td><ul class="item">
                    <li
                        v-for="(lst,ii) in entityData[1][i]"
                        :key="ii"
                        class="entityClick place"
                        :style="{'color': lst[2], 'font-size': lst[1] + 'px'}"
                        @click="emitDisplayTextOf(lst[0])"
                    >
                        {{entitiesMap[lst[0]].text}}
                        <!--{{entitiesMap[lst[0]].text}} ({{lst[1]}}x)-->
                    </li>
                </ul></td>
            </tr>
        </table>
    </div>

</template>

<script>


export default {
    name: 'AnalysisTable',
    props: {
        entitiesMap: Object,
        displayEntity: Object,
        entityData: Array
    },

    components : {
    },

    data() {
        return {
            years: []
        }
    },

    watch: {
    },

    methods: {
        emitDisplayTextOf(id) {
            this.$emit("displayTextOf", id);
        },
        buildRange() {
            for (let i=1889; i < 1917; i++) {
                this.years.push(i);
            }
        },
    },



    mounted()  {
        this.buildRange();
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
        border: 1px solid #ffffff;
        border-radius: 2px;
        box-shadow: 6px 6px #CBCBCB;
    }

    .yearGrid {
        display: grid;
        /*gap: 3px;*/
        grid-template-columns: auto auto auto;
        align-items: center;
        justify-content: start;
        grid-row-gap: 10px;
    }

    table {
        width: 100%;
    }

    table tr:nth-child(odd) {
        background-color: #f2f2f2;
    }

    .item {
        margin: 2px;

    }

    .year {
        padding: 4px;
        border: 2px solid #00000000;
    }

    .entityClick {
        display: inline-block;
        padding: 4px;
        margin: 2px;
        
        background: #FFF0;/*#EBEBEB;*/
        
    }

    .entityClick:hover {
        cursor: pointer;
        border: 3px solid #000000;
        text-decoration: underline;   
    }

    .place {
        border: 3px solid #FFF;/*#c7df7f;/*#fc7715aa;*/
        color: #000;
    }

    .person {
        border: 3px solid #00000000;
    }
</style>
