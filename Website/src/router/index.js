import { createRouter, createWebHistory } from "vue-router";
import Info from "@/components/Info.vue";
import QueryText from "@/components/Search/QueryText.vue";
import Visualizations from "@/components/Explore/Visualizations.vue";
import Analysis from "@/components/Analysis/Analysis.vue";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      name: "info",
      component: Info, //Info
    },
    {
      path: "/search",
      name: "search",
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: QueryText, //QueryText,
      //props: route => ({ searchString: route.query.q, searchClass: route.query.class, maxSize: route.query.size, singleID: route.query.id })
    },
    {
      path: "/explore/:id?",
      name: "explore",
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: Visualizations, //Visualizations,
      //props: route => ({ Id: route.query.id })
    },
    {
      path: "/analyze/:mode?",
      name: "analysis",
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: Analysis, // Analysis
    },
  ],
});

export default router;
