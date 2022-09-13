<template>
  <div class="analyzeResults">
    <h3>Search results:</h3>
    <p v-if="results.length < 1">No results</p>
    <p
      v-for="(entity, i) in results"
      :key="i"
      class="analyzeResultsItem"
      @click="emitClick(entity)"
    >
      {{ entity[1] }}
    </p>
  </div>
</template>

<script setup>
const emit = defineEmits(["showEntity"]);
defineProps({
  results: Array,
});

function emitClick(entity) {
  emit("showEntity", entity);
}
</script>

<style scoped>
.analyzeResults {
  text-align: center;
  width: 50%;
  margin-left: 25%;
  margin-bottom: 2em;
}

.analyzeResultsItem {
  padding: 4px;
  margin: 2px;
  text-decoration: underline;
  background: #ebebeb;
  border: 2px solid #00000000;
}

.analyzeResultsItem:hover {
  cursor: pointer;
  border: 2px solid #000000;
}
</style>
