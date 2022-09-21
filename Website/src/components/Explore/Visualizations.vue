<template>
    <div>
        <!--<p>Async fetching of individual graphs is not yet implemented, but it will look like this example:</p>-->
        <p>
            Through the interface below you can navigate the graph structure of our semantic web.
            Clicking the box of an entity displays the immediate neighborhood of that entity in the
            graph. You can jump to the location of the selected entity in the text by clicking the
            button "
            <img class="symbol" src="/icons/book.svg" alt="Book Symbol" />
            Show Entity in Text". If you want to start exploring the graph from a random node, click
            on the "
            <img class="symbol" src="/icons/dice-solid.svg" alt="Dice Symbol" />
            Start with random Entity" button. The entity which is currently in focus is displayed
            with
            <span class="rounded">rounded corners</span>
            (and not clickable), every other annotated entity in its neighborhood is displayed with
            <span class="sharp">sharp corners</span>
            (and clickable to set it in focus).
        </p>

        <div v-show="showerror" class="errormsg">
            <strong>{{ info }}</strong>
        </div>

        <div class="navigationElements">
            <div
                v-show="cursorId != undefined && cursorId.length > 0"
                class="navigationButton functionalButton"
                @click="emitDisplayTextOf">
                <img class="symbol" src="/icons/book.svg" alt="Book Symbol" />
                Show Entity in Text
            </div>
            <div class="navigationButton functionalButton" @click="setRandomEntityID">
                <img class="symbol" src="/icons/dice-solid.svg" alt="Dice Symbol" />
                Go to random Entity
            </div>
        </div>
        <div ref="graphVizElement">
            <inline-svg
                id="graph"
                v-show="!showerror"
                :src="svg_src"
                @loaded="svgLoaded()"
                @unloaded="svgUnloaded()"
                @error="svgLoadError()"></inline-svg>
        </div>
        <p class="statusreport">{{ info }}</p>
    </div>
</template>

<script setup>
    import InlineSvg from 'vue-inline-svg';

    import { useDataStore } from '@/stores/data';
    import { watch, ref } from 'vue';
    import { useRouter, useRoute } from 'vue-router';
    import { storeToRefs } from 'pinia';

    const router = useRouter();
    const route = useRoute();
    const { entities } = storeToRefs(useDataStore());

    const svg_src = ref(buildSVGUrl('18701')),
        showerror = ref(false),
        info = ref(''),
        graphVizElement = ref(null),
        cursorId = ref('18701');

    let listeners = [];

    watch(() => route.params, requestSVG, { deep: true, immediate: true });

    function buildSVGUrl(entityId) {
        return import.meta.env.BASE_URL + 'graphs/' + entityId + '.svg';
    }

    function requestSVG(newParams, oldParams) {
        if (process.env.NODE_ENV == 'production') {
            if (
                newParams.id != undefined &&
                newParams.id.length > 0 &&
                (oldParams == undefined || oldParams.id !== newParams.id)
            ) {
                removeListeners();
                cursorId.value = newParams.id;
                svg_src.value = buildSVGUrl(newParams.id);
            }
        }
    }

    function requestSVGinternal(event) {
        event.stopPropagation();
        const targetID = event.currentTarget.id;
        if (targetID.startsWith('N'))
            router.push({
                name: 'explore',
                params: { id: targetID.slice(1) },
            });
        //requestSVG(targetID.slice(1));
        else if (targetID.startsWith('V_'))
            router.push({ name: 'explore', params: { id: targetID.slice(2) } });
    }

    // SVG EVENTS
    function makeNodesClickable() {
        listeners = [...graphVizElement.value.getElementsByClassName('entityNode')];
        listeners.forEach((e) => {
            e.addEventListener('click', requestSVGinternal, false);
        });
    }

    function removeListeners() {
        listeners.forEach((e) => {
            e.removeEventListener('click', requestSVGinternal, false);
        });
    }

    function emitDisplayTextOf() {
        router.push({ name: 'search', query: { id: cursorId.value } });
    }

    function setRandomEntityID() {
        if (entities.value.length > 0) {
            const idx = Math.floor(Math.random() * (entities.value.length - 4000)); //The maximum is exclusive and the minimum is inclusive
            router.push({
                name: 'explore',
                params: { id: entities.value[idx].id },
            });
        } else {
            router.push({ name: 'explore', params: { id: '18701' } });
        }
    }

    // SVG STATES
    function svgLoaded() {
        makeNodesClickable();
        showerror.value = false;
        info.value = 'SVG Loaded';
    }

    function svgUnloaded() {
        info.value = 'SVG Unloaded';
    }

    function svgLoadError() {
        showerror.value = true;
        info.value = 'ERROR: Unable to load SVG!';
    }
</script>

<style scoped>
    #graph:deep(.entityNode) {
        visibility: visible;
        pointer-events: visibleFill;
    }

    #graph:deep(.entityNode:hover) {
        cursor: pointer;
    }

    #graph:deep(.entityNode:hover polygon) {
        stroke: black;
        stroke-width: 3px;
    }

    .navigationElements {
        display: block;
        width: 90%;
        margin-left: 5%;
        text-align: center;
    }

    .functionalButton {
        margin: 1ex;
        text-align: center;
    }

    .buttonRight {
        float: right;
    }

    .buttonLeft {
        float: left;
    }

    .navigationButton {
        background: #ffffff;
        padding: 1ex;
        border: 1px solid #2c3e50;
        display: inline-block;
        /*float: left;*/
    }

    .navigationButton:hover {
        cursor: pointer;
        background: #ebebeb;
    }

    .statusreport {
        font-style: italic;
    }

    .symbol {
        display: inline;
        height: 0.9em;
    }

    .rounded {
        display: inline-block;
        border: 1px solid black;
        border-radius: 1em;
        padding: 2px;
    }

    .sharp {
        display: inline-block;
        border: 1px solid black;
        border-radius: 0;
        padding: 2px;
    }
</style>
