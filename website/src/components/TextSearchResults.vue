<template>
    <div>
        <p>Found {{results.length &lt; 40 ? results.length : '>'+results.length}} {{results.length === 1 ? 'Entity': 'Entities'}}</p>
        <div 
            class="groupResult"
            v-for="(list,i) in groupedResults"
            :key="i"
        >
            <h3>{{list[0].institution}} {{list[0].year &gt; 0 ? list[0].year : ''}} ({{list.length}} mentions)</h3>
            <TextEntityCard
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
            groupOrdering: []
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
            this.results.forEach(element => {
                let group = element.txt_id;
                let groupIdx = this.groupOrdering.indexOf(group);

                if (groupIdx > -1) {
                    this.groupedResults[groupIdx].push(element);
                } else {
                    this.groupedResults.push([element,]);
                    this.groupOrdering.push(group);
                }
            });
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

</style>
