$(function() {
  var model = {
    init: function() {
      if (!localStorage.cats) {
        $.getJSON("cats.json", function(data) {
          localStorage.cats = JSON.stringify(data);
          localStorage.currentCat = 0;
          localStorage.adminStatus = "false";
        });
      }
    },

    add: function(obj) {
      var data = JSON.parse(localStorage.cats);
      data.push(obj);
      localStorage.cats = JSON.stringify(data);
    },

    getAllCats: function() {
      return JSON.parse(localStorage.cats);
    },

    getCat: function(ind) {
      cats = JSON.parse(localStorage.cats);
      return cats[ind];
    },

    setCurrentCat: function(ind) {
      localStorage.currentCat = ind;
    },

    getCurrentCat: function(ind) {
      return localStorage.currentCat;
    },

    updateClicks: function(ind, clicks) {
      cats = JSON.parse(localStorage.cats);
      cats[ind]["clicks"] = clicks;
      localStorage.cats = JSON.stringify(cats);
    },

    updateCat: function(ind, name, url, clicks) {
      cats = JSON.parse(localStorage.cats);
      cats[ind]["name"] = name;
      cats[ind]["url"] = url;
      cats[ind]["clicks"] = clicks;
      localStorage.cats = JSON.stringify(cats);
    },

    setAdminStatus: function(status) {
      localStorage.adminStatus = status;
    },

    getAdminStatus: function() {
      return localStorage.adminStatus;
    }
  };

  var octopus = {
    addNewCat: function(catStr) {
      model.add({
        content: catStr
      });
      view.render();
    },

    getCats: function() {
      return model.getAllCats();
    },

    getCat: function(ind) {
      return model.getCat(ind);
    },

    showCat: function(ind) {
      model.setCurrentCat(ind);
      var cat = model.getCat(ind);
      view_cat.render(cat);
      view_admin.render(cat);
    },

    incrClicks: function() {
      var ind = model.getCurrentCat();
      var cat = model.getCat(ind);
      var newClicks = cat["clicks"] + 1;
      model.updateClicks(ind, newClicks);
      view_cat.updateClicks(newClicks);
      view_admin.updateClicks(newClicks);
    },

    showAdmin: function() {
      model.setAdminStatus("true");
      view_admin.showAdmin();
    },

    hideAdmin: function() {
      model.setAdminStatus("false");
      view_admin.hideAdmin();
    },

    updateCat: function(name, url, clicks) {
      var ind = model.getCurrentCat();
      model.updateCat(ind, name, url, clicks);
      this.showCat(ind);
      view_list.render();
      view_admin.hideAdmin();
    },

    init: function() {
      model.init();
      view_list.init();
      view_cat.init();
      view_admin.init();
      var ind = model.getCurrentCat();
      this.showCat(ind);
      var adminShown = model.getAdminStatus();
      if (adminShown == "true") {
        this.showAdmin();
      }
    }
  };

  var view_list = {
    init: function() {
      this.catList = $("#cats-list");
      this.joinStr = "\n        ";
      view_list.render();
    },

    render: function() {
      var htmlStr = "";
      var joinStr = this.joinStr;
      $.each(octopus.getCats(), function(key, val) {
        htmlStr +=
          joinStr +
          '<li id="cat-item-' +
          key +
          '"><a href="#">' +
          val["name"] +
          "</li>";
      });
      this.catList.html(htmlStr);
      $.each(octopus.getCats(), function(key, val) {
        $("#cat-item-" + key).click(function(e) {
          octopus.showCat(key);
        });
      });
    }
  };

  var view_cat = {
    init: function() {
      this.catName = $("#cat-name");
      this.catImage = $("#cat-image");
      this.catClicks = $("#cat-clicks");
      this.catImage.click(function(e) {
        octopus.incrClicks();
      });
    },

    render: function(cat) {
      this.catName.html(cat["name"]);
      this.catImage.attr("src", cat["url"]);
      this.catClicks.html(cat["clicks"]);
    },

    updateClicks: function(clicks) {
      this.catClicks.html(clicks);
    }
  };

  var view_admin = {
    init: function() {
      this.adminForm = $("#admin-form");
      this.catName = $("#admin-name");
      this.catUrl = $("#admin-url");
      this.catClicks = $("#admin-clicks");
      $("#admin-button").click(function(e) {
        octopus.showAdmin();
      });
      $("#admin-cancel").click(function(e) {
        octopus.hideAdmin();
        e.preventDefault();
      });
      $("#admin-form").submit(function(e) {
        octopus.updateCat(
          view_admin.catName.val(),
          view_admin.catUrl.val(),
          Number(view_admin.catClicks.val())
        );
        e.preventDefault();
      });
    },

    render: function(cat) {
      this.catName.val(cat["name"]);
      this.catUrl.val(cat["url"]);
      this.catClicks.val(cat["clicks"]);
    },

    showAdmin: function() {
      this.adminForm.show();
    },

    hideAdmin: function() {
      this.adminForm.hide();
    },

    updateClicks: function(clicks) {
      this.catClicks.val(clicks);
    }
  };

  octopus.init();
});
