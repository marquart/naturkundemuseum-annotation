<template>
    <div>
        <p>Async fetching of individual graphs is not yet implemented, but it will look like this example:</p>
        <img class="graph"
            src="../assets/11492.svg"
            alt="Neighborhood graph for Entity 5535"
        />
    </div>
</template>

<script>
export default {
  name: 'Visualizations',
  props: {
      entityId: String
  },

}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
    .graph {
        
    }
</style>
