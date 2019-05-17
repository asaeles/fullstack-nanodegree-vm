class Cat {
  name = "";
  url = "";
  index = 0;
  clicks = 0;

  constructor(name, url, index = 0, initial_clicks = 0) {
    this.name = name;
    this.url = url;
    this.index = index;
    this.clicks = initial_clicks;
  }

  increment(num = 1) {
    this.clicks = this.clicks + num;
    console.log(this.clicks);
    $("#cat-clicks").text(this.clicks);
  }

  template() {
    var template = `
    <div id="cat-div">
      <h3 id="cat-name">${this.name}</h3>
      <img
        id="cat-image"
        style="max-height: 300px;"
        src="${this.url}"
        alt="Cute cat image"
      />
      <p>Number of clicks:</p>
      <h2 id="cat-clicks">${this.clicks}</h2>
    </div>
  `;
    return template;
  }
}
