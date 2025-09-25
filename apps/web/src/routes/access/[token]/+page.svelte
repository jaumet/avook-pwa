<script lang="ts">
  import AccessPage from '../AccessPage.svelte';

  type PageData = import('./$types').PageData;

  export let data: PageData;
</script>

<AccessPage {data} />

