<template>
    <div>
        <QueryTextInfo />
        <p>
            With this form it is possible to search the words annotated so far and/or filter the
            results by semantic class via the search options.
        </p>
        <div v-if="loading"><strong>LOADING...</strong></div>
        <div v-else>
            <EntitySearcher :moreSearchOptions="true" route="search" :params="{}" />

            <!--
            <div v-show="loading" class="loadingMsg">
                <img class="loadingSymb" src="../assets/otter-solid.svg" alt="Loading Symbol"/>
                <p>Searching...</p>
            </div>
            

            <div id="navigationElements">
                <div v-if="historyCursor>0" class="navigationButton buttonLeft" @click="navigateHistory(-1)">🡸 Go Back</div>
                <div v-if="historyCursor<history.length-1" class="navigationButton buttonRight" @click="navigateHistory(1)" >Go Forward 🡺</div>
            </div>
            -->
            <TextSearchResults v-show="showResults" :results="searchResults" />
        </div>
    </div>
</template>

<script setup>
    import { useDataStore } from '@/stores/data';
    import { watch, ref } from 'vue';
    import { useRoute } from 'vue-router';
    import { storeToRefs } from 'pinia';

    import EntitySearcher from '@/components/EntitySearcher.vue';
    import TextSearchResults from '@/components/Search/TextSearchResults.vue';
    import QueryTextInfo from '@/components/Search/QueryTextInfo.vue';

    const { entities, entitiesMap, loading } = storeToRefs(useDataStore());
    const searchResults = ref([]),
        showResults = ref(false);
    const route = useRoute();
    const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

    watch(() => route.query, processProps, { deep: true, immediate: true });

    function processProps() {
        if (route.query.id != undefined && route.query.id !== '') queryOneEntity();
        else if (route.query.q != undefined || route.query.class != undefined) query();
    }

    async function query() {
        while (loading.value) await sleep(500);
        searchResults.value = Array.from(filterEntities());
        showResults.value = true;
    }

    function validEntity(entity) {
        return (
            entity.type.indexOf(route.query.class) != -1 &&
            entity.search_string.indexOf(route.query.q) != -1
        );
    }

    function* filterEntities() {
        let maxSize = route.query.size;
        if (route.query.size > entities.value.length) maxSize = entities.value.length;

        let count = 0;
        /* BACKWARDS SEARCH:*/
        let i = entities.value.length - 1;
        while (count < maxSize && i >= 0) {
            if (validEntity(entities.value[i])) {
                //(this.entities[i].search_string.indexOf(string) != -1 && this.entities[i].type.indexOf(this.sourceSearchClass) != -1)
                yield entities.value[i];
                count++;
            }
            i--;
        }
    }

    async function queryOneEntity() {
        while (loading.value) await sleep(500);
        searchResults.value = [entitiesMap.value[route.query.id]];
        showResults.value = true;
    }
</script>

<style scoped>
    #navigationElements {
        display: block;
        width: 90%;
        margin-left: 5%;
    }

    .navigationButton {
        background: #ffffff;
        padding: 1ex;
        border: 1px solid #2c3e50;
        display: inline-block;
    }

    .navigationButton:hover {
        cursor: pointer;
        background: #ebebeb;
    }

    .buttonRight {
        float: right;
    }

    .buttonLeft {
        float: left;
    }

    .loadingMsg {
        text-align: center;
    }

    .loadingSymb {
        display: inline-block;
        width: 8em;
        height: 8em;

        animation-name: loading;
        animation-duration: 3s;
        animation-iteration-count: infinite;
    }

    @keyframes loading {
        0% {
            transform: rotate(0deg);
        }
        100% {
            transform: rotate(360deg);
        }
    }

    @media screen and (max-width: 700px) {
        .searchField {
            width: 100%;
            margin-left: 0%;
        }
    }
</style>
