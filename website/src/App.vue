<template>
  <div id="app">
    <div id="heading">
      <img src="./assets/mfn-logo.png" alt="Naturkundemuseum Logo">
      <div id="heading-text">
        <h1>Provenance research under the spotlight</h1>
        <h2>Digital Edition of the Annual Reports of the Museum 1887–1915 and 1928–1938</h2>
      </div>
    </div>
    <!--<Column msg="Welcome to Your Vue.js App"/>-->
    <div class="content" id="navigation">
      <div class="navmode">
        <div class="selectmode" :style="infoNavStyle" @click="navigate(0)">Info</div>
        <div class="selectmode" :style="searchNavStyle" @click="navigate(1)">Construct Query</div>
      </div>
    </div>

    <Info class="content" v-show="mode == 0" />
    <Query class="content" v-show="mode == 1" />
  </div>
</template>

<script>
//import HelloWorld from './components/Column.vue'
import Info from './components/Info.vue'
import Query from './components/Query.vue'

export default {
  name: 'App',
  components: {
    Info,
    Query
  },
  data() {
    return {
      infoNavStyle: {background: '#ffffff'},
      searchNavStyle: {background: '#EBEBEB'},
      mode: 0,
    }
  },

  methods: {
    navigate(mode) {
      this.mode = mode;
      if (this.mode == 0) {
        this.infoNavStyle.background = '#ffffff';
        this.searchNavStyle.background = '#EBEBEB';
      } else if (this.mode == 1) {
        this.infoNavStyle.background = '#EBEBEB';
        this.searchNavStyle.background = '#ffffff';
      }

    },

  },
}
</script>

<style>
  /*@import url('https://fonts.googleapis.com/css2?family=Open+Sans&display=swap');*/
  @import url('https://fonts.googleapis.com/css2?family=Titillium+Web&display=swap');

  body {
    /*background: linear-gradient(to bottom, #ffffff,  #f0f0f0);*/
    background: #f0f0f0;
    background-attachment: fixed;
    background-size: cover;
    margin: 0;
    height: 100%;
  }

  #app {
    font-family: "Titillium Web", "Open Sans", "Trade Gothic Next LT", Helvetica, Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    color: #2c3e50;
    margin-top: 20px;
  }

  .content {
    margin-left: 5%;
    margin-right: 5%;
    text-align: left;
    width: 90%;
    display: block;
    line-height: 1.5;
  }

  #navigation {
    border-bottom: 2px solid #7da30b;
  }

  .navmode {
    width: 100%;
    height: auto;

  }

  .selectmode {
    width: 50%;
    font-size: 1.2em;
    font-family: inherit;
    display: inline-block;
    text-align: center;
    background: #ffffff;
    color: black;
    padding-top: 0.5em;
    padding-bottom: 0.5em;
  }

  .selectmode:hover {
      cursor: pointer;
    }

  img {

  }

  #heading {
    width: 90%;
    margin: 1%;
    display: grid;
    grid: 
      'logo headingText';
    align-items: center;
  }

  h1 {
    font-weight: bold;
    display: inherit;
  }

  h2 {
    font-weight: normal;
    display: inherit;
  }

  #heading-text {
    text-align: left;
    /*float: left;
    transform: translate(0, 100px);*/
    grid-area: 'headingText';
  }

  #heading img {
    height: 270px;
    grid-area: 'logo';
    /*position: relative;
    display: inline;
    float:left;
    margin-right: 10px;*/
  }
</style>
