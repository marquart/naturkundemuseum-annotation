<template>
    <div>
        <p>Async fetching of individual graphs is not yet implemented, but it will look like this example:</p>
        <a href="../assets/11536.svg" target="_blank">
            <img class="graph"
                src="../assets/11536.svg"
                alt="Neighborhood graph for Entity 11536"
            />
        </a>
    </div>
</template>

<script>
export default {
  name: 'Visualizations',
  props: {
      entityId: String
  },

  data() {
      return {
          svg_src: "../assets/11536.svg"
      }
  },

}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
    .graph {
        
    }
</style>
