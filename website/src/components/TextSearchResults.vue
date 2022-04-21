<template>
    <div>
        <p>Found {{results.length &lt; 40 ? results.length : '>'+results.length}} {{results.length === 1 ? 'Entity': 'Entities'}}</p>
        <div 
            class="groupResult"
            v-for="(list,i) in groupedResults"
            :key="i"
            
        >
            <h3 @click="toggleResults(i)">{{groupState[i] ? '🡻': '🡺'}}  {{list[0].institution}} {{list[0].year &gt; 0 ? list[0].year : ''}} ({{list.length}} {{list.length === 1 ? 'mention': 'mentions'}})</h3>
            <TextEntityCard
                v-show="groupState[i] === true"
                @showOneEntity="showOneEntity"
                @displayGraphOf="emitDisplayGraphOf"
                v-for="result in list"
                :key="result.id"
                :entity="result"
                :texts="texts"
            />
        </div>
    </div>
</template>

<script>
import TextEntityCard from './TextEntityCard.vue'

export default {
    name: 'TextSearchResults',
    components: {
        TextEntityCard
    },
    props: {
        results: Array,
        texts: Object
    },
    data() {
        return {
            groupedResults: [],
            groupOrdering: [],
            groupState: [], // Results of the group at groupIDX are displayed (because user has opened it)
        }
    },

    emits: ['showOneEntity', 'displayGraphOf'],

    methods: {
        showOneEntity(item) {
            this.$emit('showOneEntity', item);
        },
        emitDisplayGraphOf(item_id) {
            this.$emit('displayGraphOf', item_id);
        },
        groupResults() {
            this.groupedResults = [];
            this.groupOrdering = [];
            this.groupState = [];
            this.results.forEach(element => {
                let group = element.txt_id;
                let groupIdx = this.groupOrdering.indexOf(group);

                if (groupIdx > -1) {
                    this.groupedResults[groupIdx].push(element);
                } else {
                    this.groupedResults.push([element,]);
                    this.groupOrdering.push(group);
                    this.groupState.push(false);
                }
            });
        },
        toggleResults(idx) {
            if (0 <= idx && idx < this.groupState.length) {
                if (this.groupState[idx]) this.groupState[idx] = false;
                else this.groupState[idx] = true;
            }
        },
    },

    watch: {
        results() {
            this.groupResults();
        }
    },
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
    p {
        text-align: center;
    }

    .groupResult {
        margin: 1em;
        padding: 1em;
        background: #ffffff;
        border: 1px solid #ffffff;
        border-radius: 2px;
        box-shadow: 6px 6px #CBCBCB;
    }

    h3:hover {
        cursor: pointer;
    }

</style>
