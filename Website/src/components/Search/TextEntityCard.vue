<template>
  <div class="card">
    <TextSnippet
      :textidx="props.entity.txt_id"
      :lineidx="props.entity.line_idx"
      :pageline="props.entity.line"
    />
    <div class="semanticData">
      <h2>Semantic Entity</h2>
      <h3 class="typeHeading">{{ props.entity.text }}</h3>
      <h4 class="entityText cidocLink tooltip">
        <a
          :href="`https://cidoc-crm.org/html/cidoc_crm_v7.1.1.html#${props.entity.short_type}`"
          target="_blank"
          ><p class="tooltiptext">{{ cidocHoverText }}</p>
          {{ props.entity.type }}</a
        >
      </h4>
      <div
        class="itemLink tooltip"
        @click="emitDisplayGraphOf(props.entity.id)"
      >
        <p class="tooltiptext">{{ graphHoverText }}</p>
        <img class="symbol" src="/icons/zoom.svg" alt="Graph Symbol" /> Show
        Neighborhood Graph
      </div>
      <div class="numericTable">
        <!--<div class="ncell">Source:</div>-->
        <div class="ncell">
          {{ props.entity.citation ? props.entity.citation : "—" }}
        </div>

        <!--<div class="ncell"></div>-->
        <div v-show="props.entity.citation.length > 0" class="ncell tooltip">
          <a :href="props.entity.url" target="_blank"
            ><p class="tooltiptext">{{ imageHoverText }}</p>
            {{ props.entity.url }}</a
          >
        </div>
        <!--
                <div class="ncell">Page:</div>
                <div class="ncell">{{props.entity.original_page &gt; 0 ? props.entity.original_page : '—'}}</div>

                <div class="ncell">Line:</div>
                <div class="ncell">{{props.entity.line &gt; -1 ? props.entity.line : '—'}}</div>

                <div class="ncell">Year:</div>
                <div class="ncell">{{props.entity.year &gt; 0 ? props.entity.year : '—'}}</div>

                <div class="ncell">Institution:</div>
                <div class="ncell">{{props.entity.institution}}</div>
                -->
      </div>

      <h4>Predecessors (incoming Relations)</h4>
      <div
        v-show="
          props.entity.incomingProps != undefined &&
          props.entity.incomingProps.length > 0
        "
        class="propTable"
      >
        <!--<div class="propItem tableHeading">Neighbor props.entity</div><div class="propItem"></div><div class="propItem tableHeading">CIDOC CRM Property</div><div class="propItem"></div>-->
        <template v-for="(prop, i) in props.entity.incomingProps" :key="i">
          <!--<div class="propItem">{{prop.source.type}}:</div>-->
          <div
            class="propItem itemLink tooltip"
            @click="showOneEntity(prop.source.id)"
          >
            <p class="tooltiptext">{{ neighborHoverText }}</p>
            {{ prop.source.text }}
          </div>
          <div class="propItem">🡺</div>
          <div class="propItem cidocLink tooltip">
            <a
              :href="`https://cidoc-crm.org/html/cidoc_crm_v7.1.1.html#${prop.short_type}`"
              target="_blank"
              ><p class="tooltiptext">{{ cidocHoverText }}</p>
              {{ prop.type }}</a
            >
          </div>
          <div class="propItem">🡺</div>
        </template>
      </div>
      <h4>Successors (outgoing Relations)</h4>
      <div
        v-show="
          props.entity.outgoingProps != undefined &&
          props.entity.outgoingProps.length > 0
        "
        class="propTable"
      >
        <!--<div class="propItem"></div><div class="propItem tableHeading">CIDOC CRM Property</div><div class="propItem"></div><div class="propItem tableHeading">Neighbor props.entity</div>-->
        <template v-for="(prop, i) in props.entity.outgoingProps" :key="i">
          <div class="propItem">🡺</div>
          <div class="propItem cidocLink tooltip">
            <a
              :href="`https://cidoc-crm.org/html/cidoc_crm_v7.1.1.html#${prop.short_type}`"
              target="_blank"
              ><p class="tooltiptext">{{ cidocHoverText }}</p>
              {{ prop.type }}</a
            >
          </div>
          <div class="propItem">🡺</div>
          <!--<div class="propItem">{{prop.target.type}}:</div>-->
          <div
            class="propItem itemLink tooltip"
            @click="showOneEntity(prop.target.id)"
          >
            <p class="tooltiptext">{{ neighborHoverText }}</p>
            {{ prop.target.text }}
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from "vue-router";
import TextSnippet from "@/components/Search/TextSnippet.vue";

const router = useRouter();
const props = defineProps({
  entity: Object,
});

const cidocHoverText = "Read definition in CIDOC documentation",
  graphHoverText =
    "Display the entity embedded in a visualization of our knowledge graph",
  neighborHoverText = "Jump to this entity",
  imageHoverText = "Go to digitized image of this page";

function showOneEntity(item_id) {
  router.push({ name: "search", query: { id: item_id } });
}

function emitDisplayGraphOf(item_id) {
  router.push({ name: "explore", params: { id: item_id } });
}
</script>

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
  margin-left: 1ex;
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
  width: 96%;
  margin-left: 2%;
  margin-bottom: 1.5em;
  /*
        background: #F6F6F6;
        border: 0.8ex solid #7da30b77;
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

.tableHeading {
  font-weight: 600;
  padding-bottom: 3px;
}

.itemLink {
  text-decoration: underline;
  background: #ebebeb;
  border: 1px solid #00000000;
}

.itemLink:hover {
  cursor: pointer;
  border: 1px solid #000000;
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

.tooltiptext {
  visibility: hidden;
  background-color: white;
  color: #000;
  text-align: center;
  padding: 3px;
  border-radius: 6px;
  border: 1px solid black;
  font-weight: 100;
  display: block;
  margin-top: 2em;

  /* Position the tooltip text - see examples below! */
  position: absolute;
  z-index: 1;
}

.tooltip:hover .tooltiptext {
  visibility: visible;
}

@media screen and (max-width: 700px) {
  .card {
    grid-template-columns: auto;
  }
}
</style>
