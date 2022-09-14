<template>
    <div>
        <p>
            Found
            {{props.results.length &lt; 40 ? props.results.length : '>'+ props.results.length}}
            {{ props.results.length === 1 ? 'Entity' : 'Entities' }}
        </p>
        <div class="groupResult" v-for="(list, i) in groupedResults" :key="i">
            <h3 @click="toggleResults(i)">
                {{ groupState[i] ? '🡻' : '🡺' }} {{ list[0].institution }}
                {{list[0].year &gt; 0 ? list[0].year : ''}} ({{ list.length }}
                {{ list.length === 1 ? 'entity' : 'entities' }},
                {{ sumMentions(list) }} mentions)
            </h3>
            <TextEntityCard
                v-show="groupState[i] === true"
                v-for="result in list"
                :key="result.id"
                :entity="result" />
        </div>
    </div>
</template>

<script setup>
    import { watch, ref } from 'vue';
    import TextEntityCard from '@/components/Search/TextEntityCard.vue';

    const props = defineProps({
        results: Array,
    });

    const groupedResults = ref([]),
        groupOrdering = ref([]),
        groupState = ref([]);

    watch(() => props.results, groupResults, { immediate: true });

    function groupResults() {
        let tmpGroupedResults = [],
            tmpGroupOrdering = [],
            tmpGroupState = [];

        props.results.forEach((element) => {
            let group = element.txt_id;
            let groupIdx = tmpGroupOrdering.indexOf(group);

            if (groupIdx > -1) {
                tmpGroupedResults[groupIdx].push(element);
            } else {
                tmpGroupedResults.push([element]);
                tmpGroupOrdering.push(group);
                tmpGroupState.push(false);
            }
        });
        if (tmpGroupState.length === 1) tmpGroupState[0] = true; //entities in only one document found
        groupedResults.value = tmpGroupedResults;
        groupOrdering.value = tmpGroupOrdering;
        groupState.value = tmpGroupState;
    }

    function toggleResults(idx) {
        if (0 <= idx && idx < groupState.value.length) {
            if (groupState.value[idx]) groupState.value[idx] = false;
            else groupState.value[idx] = true;
        }
    }

    function sumMentions(list) {
        return list.reduce((accu, it) => accu + it.mentions, 0);
    }
</script>

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
        box-shadow: 6px 6px #cbcbcb;
    }

    h3:hover {
        cursor: pointer;
    }
</style>
