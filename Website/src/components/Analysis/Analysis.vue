<template>
    <div>
        <div v-show="loadError" class="errormsg">
            <strong>{{ errorMsg }}</strong>
        </div>
        <p>
            As we annotated the acqusitions of objects over many years, it made
            sense to develop a tool which can be used to analyze the more
            consistent entities over the years more abstractly. It turned out
            that suppliers, original locations and the receiving collections are
            the most consistent information points. With the search bar below
            you can search for entities of either one of the three and get an
            overview of which of the entities of the other two types are
            connected to it over the years.
        </p>
        <p>
            The color and size indicate how much the author of the Chronik
            elaborated on each underlying acquisition compared to other
            acquisitions and can be interpreted as a level of appreciation of
            this specific transaction in the context of the gift economy. The
            more information the author packed into the description of a
            transaction, the higher the weight we gave it. The information
            points we have considered are primarily original locations (e.g.
            <span class="entityClick" @click="emitDisplayTextOf('11719')">
                "Dar-es-Salaam"
            </span>
            ) & taxonomic classifications (e.g.
            <span class="entityClick" @click="emitDisplayTextOf('23459')">
                "Hirundo rustica"
            </span>
            ) of the objects transferred and especially subjective assessments
            about the value and dimensions, like
            <span class="entityClick" @click="emitDisplayTextOf('44789')">
                "sauber präpariert"
            </span>
            ,
            <span class="entityClick" @click="emitDisplayTextOf('34588')">
                "überaus wertvoll"
            </span>
            or
            <span class="entityClick" @click="emitDisplayTextOf('32397')">
                "sehr große Anzahl"
            </span>
            .
        </p>
        <p>
            The distribution of these weights over all identified acquisitions
            looks like this:
        </p>
        <AcquisitionsWeights />
        <div class="modeselection">
            <p
                class="mode"
                :style="[mode === 'Suppliers' ? focusStyle : unFocusStyle]"
                @click="goTo('Suppliers')">
                Suppliers
            </p>
            <p
                class="mode"
                :style="[mode === 'Locations' ? focusStyle : unFocusStyle]"
                @click="goTo('Locations')">
                Locations
            </p>
            <p
                class="mode"
                :style="[mode === 'Collections' ? focusStyle : unFocusStyle]"
                @click="goTo('Collections')">
                Collections
            </p>
        </div>
        <EntitySearcher
            :moreSearchOptions="false"
            route="analysis"
            :params="{ mode: mode }" />

        <AnalysisSearchResults
            v-show="showResults"
            :results="searchResults"
            @showEntity="showEntity" />

        <AnalysisTable
            v-if="showTable"
            :displayEntity="displayEntity"
            :entityData="cursorResult" />
    </div>
</template>

<script setup>
    import { watch, ref, onMounted } from 'vue';
    import { useRouter, useRoute } from 'vue-router';

    import AcquisitionsWeights from '@/components/SVG/AcquisitionsWeights.vue';
    import AnalysisTable from '@/components/Analysis/AnalysisTable.vue';
    import EntitySearcher from '@/components/EntitySearcher.vue';
    import AnalysisSearchResults from '@/components/Analysis/AnalysisSearchResults.vue';

    const router = useRouter();
    const route = useRoute();

    const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

    const mode = ref('Suppliers'),
        focusStyle = { background: '#ffffff', color: '#7da30b' },
        unFocusStyle = { background: '#EBEBEB' },
        loadError = ref(false),
        errorMsg = ref(''),
        dataLoaded = ref(false),
        personsLookup = ref({}),
        locationsLookup = ref({}),
        collectionsLookup = ref({}),
        personTable = ref({}),
        locationsTable = ref({}),
        collectionsTable = ref({}),
        maxSize = 40,
        showResults = ref(false),
        showTable = ref(false),
        searchResults = ref([]),
        cursorResult = ref({}),
        displayEntity = ref({});

    watch(() => route.params, navigate, { deep: true, immediate: true });
    watch(() => route.query, query, { deep: true, immediate: true });

    function goTo(para) {
        router.push({ name: 'analysis', params: { mode: para } });
    }

    async function navigate(newParams, oldParams) {
        if (
            newParams != undefined &&
            newParams.mode != undefined &&
            (oldParams == undefined || oldParams.mode !== newParams.mode)
        ) {
            showResults.value = false;
            mode.value = newParams.mode;
            while (!dataLoaded.value) await sleep(200);
            if (!showResults.value) showEntity(personsLookup.value[0]);
        }
    }

    function emitDisplayTextOf(entity_id) {
        router.push({ name: 'search', query: { id: entity_id } });
    }

    async function query(newQuery) {
        if (!dataLoaded.value) dataLoaded.value = await fetchData();
        if (dataLoaded.value && newQuery.q != undefined) {
            searchResults.value = [];

            if (mode.value === 'Suppliers')
                filterEntities(personsLookup.value, newQuery.q);
            else if (mode.value === 'Locations')
                filterEntities(locationsLookup.value, newQuery.q);
            else if (mode.value === 'Collections')
                filterEntities(collectionsLookup.value, newQuery.q);

            showResults.value = true;
        }
    }

    function filterEntities(lookup, searchString) {
        let count = 0;
        let cursor = null;
        /* BACKWARDS SEARCH:*/
        let i = lookup.length - 1;
        while (count < maxSize && i >= 0) {
            cursor = lookup[i];
            if (cursor[0].indexOf(searchString) != -1) {
                searchResults.value.push(cursor);
                count++;
            }
            i--;
        }
    }

    async function showEntity(entity) {
        showResults.value = false;
        while (!dataLoaded.value) await sleep(100);
        displayEntity.value = entity;
        if (mode.value === 'Suppliers')
            cursorResult.value = personTable.value[entity[1]];
        else if (mode.value === 'Locations')
            cursorResult.value = locationsTable.value[entity[1]];
        else if (mode.value === 'Collections')
            cursorResult.value = collectionsTable.value[entity[1]];

        showTable.value =
            cursorResult.value != undefined && displayEntity.value != undefined;
    }

    async function fetchData() {
        const rslt = await Promise.all([
            fetch(import.meta.env.BASE_URL + 'data/Persons.json', {
                headers: {
                    'Content-type': 'application/json',
                    charset: 'utf-8',
                },
            }).then((res) => (res.ok && res.json()) || Promise.reject(res)),
            fetch(import.meta.env.BASE_URL + 'data/Locations.json', {
                headers: {
                    'Content-type': 'application/json',
                    charset: 'utf-8',
                },
            }).then((res) => (res.ok && res.json()) || Promise.reject(res)),
            fetch(import.meta.env.BASE_URL + 'data/Collections.json', {
                headers: {
                    'Content-type': 'application/json',
                    charset: 'utf-8',
                },
            }).then((res) => (res.ok && res.json()) || Promise.reject(res)),
        ]).then((data) => {
            // handle data array here
            if (
                data == undefined ||
                data.length != 3 ||
                data[0] == undefined ||
                data[1] == undefined ||
                data[2] == undefined
            ) {
                errorMsg.value = "Couldn't fetch data from backend!";
                loadError.value = true;
                return false;
            } else {
                loadError.value = false;
                //Persons
                personsLookup.value = data[0][0];
                personTable.value = data[0][1];
                //Locations
                locationsLookup.value = data[1][0];
                locationsTable.value = data[1][1];
                //Collections
                collectionsLookup.value = data[2][0];
                collectionsTable.value = data[2][1];
                dataLoaded.value = true;

                if (!showResults.value) showEntity(personsLookup.value[0]);
                return true;
            }
        });
        return rslt;
    }

    onMounted(fetchData);
</script>

<style scoped>
    .modeselection {
        width: 80%;
        margin-left: 10%;
        display: grid;
        grid-template-columns: auto auto auto;
        align-content: center;
    }

    .mode {
        font-size: 1.2em;
        font-family: inherit;
        text-align: center;
        background: #ffffff;
        color: black;
        padding-top: 0.5em;
        padding-bottom: 0.5em;
        border-bottom: 5px solid #00000000;
    }

    .mode:hover {
        cursor: pointer;
        border-bottom: 5px solid #7da30b;
        color: #7da30b;
    }

    #button {
        box-sizing: border-box;
        display: inline;
        font-size: 1.2em;
        margin: 1.2em;
        font-family: inherit;
        color: inherit;
        cursor: pointer;
        text-align: center;
        width: 30%;
        background: #ffffff;
        margin-left: 35%;
        border: 1px solid #2c3e50;
    }

    #button:hover {
        background: #ebebeb;
    }

    .entityClick {
        display: inline-block;
        padding: 1px;
        margin: 2px;
        border: 1px solid #f2f2f2;
        background: #fff0; /*#EBEBEB;*/
        color: #7da30b;
    }

    .entityClick:hover {
        cursor: pointer;
        border: 1px solid #000000;
        text-decoration: underline;
    }
</style>
