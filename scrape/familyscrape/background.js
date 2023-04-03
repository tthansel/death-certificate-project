/*
On page action click, navigate the corresponding tab to the cat gifs.
*/
browser.pageAction.onClicked.addListener((tab) => {
  console.log("This still appears not to be working")
  browser.tabs.sendMessage(tab.id, "");
});
