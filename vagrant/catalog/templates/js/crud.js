// This script contains all the AJAX functions
//  required to edit (create, update & delete)
//  categories and their items

// All requests use the token authentication

function addCategory(name, picture, description) {
  if (!name || name == "") {
    console.log('addCategory: Mandatory parameter "name" missing');
    return false;
  }
  if (picture === undefined) {
    picture = "";
  }
  if (description === undefined) {
    description = "";
  }
  loadingOn();
  $.ajax({
    type: "POST",
    url: "/api/v1/categories",
    contentType: "application/json",
    beforeSend: function(xhr) {
      xhr.setRequestHeader(
        "Authorization",
        "Basic " + btoa(Cookies.get("token") + ":blank")
      );
    },
    data: JSON.stringify({
      name: name,
      picture: picture,
      description: description
    }),
    success: function(data) {
      $.get("/api/v1/catalog", function(data) {
        refreshCatalog(data);
        loadingOff();
      });
    },
    error: function(data) {
      loadingOff();
      return false;
    }
  });
}

function updateCategory(id, name, picture, description) {
  if (!id || id == "") {
    console.log('updateCategory: Mandatory parameter "id" missing');
    return false;
  }
  if (!name || name == "") {
    console.log('updateCategory: Mandatory parameter "name" missing');
    return false;
  }
  if (picture === undefined) {
    picture = "";
  }
  if (description === undefined) {
    description = "";
  }
  loadingOn();
  $.ajax({
    type: "PUT",
    url: "/api/v1/categories/" + id,
    contentType: "application/json",
    beforeSend: function(xhr) {
      xhr.setRequestHeader(
        "Authorization",
        "Basic " + btoa(Cookies.get("token") + ":blank")
      );
    },
    data: JSON.stringify({
      name: name,
      picture: picture,
      description: description
    }),
    success: function(data) {
      $.get("/api/v1/catalog", function(data) {
        refreshCatalog(data);
        loadingOff();
      });
    },
    error: function(data) {
      loadingOff();
      return false;
    }
  });
}

function deleteCategory(id) {
  if (!id || id == "") {
    console.log('deleteCategory: Mandatory parameter "id" missing');
    return false;
  }
  loadingOn();
  $.ajax({
    type: "DELETE",
    url: "/api/v1/categories/" + id,
    contentType: "application/json",
    beforeSend: function(xhr) {
      xhr.setRequestHeader(
        "Authorization",
        "Basic " + btoa(Cookies.get("token") + ":blank")
      );
    },
    success: function(data) {
      $.get("/api/v1/catalog", function(data) {
        refreshCatalog(data);
        loadingOff();
      });
    },
    error: function(data) {
      loadingOff();
      return false;
    }
  });
}

function addItem(name, category_id, picture, description) {
  if (!name || name == "") {
    console.log('addCategory: Mandatory parameter "name" missing');
    return false;
  }
  if (!category_id || category_id == "") {
    console.log('addCategory: Mandatory parameter "category_id" missing');
    return false;
  }
  if (picture === undefined) {
    picture = "";
  }
  if (description === undefined) {
    description = "";
  }
  loadingOn();
  $.ajax({
    type: "POST",
    url: "/api/v1/items",
    contentType: "application/json",
    beforeSend: function(xhr) {
      xhr.setRequestHeader(
        "Authorization",
        "Basic " + btoa(Cookies.get("token") + ":blank")
      );
    },
    data: JSON.stringify({
      name: name,
      picture: picture,
      description: description,
      category_id: category_id
    }),
    success: function(data) {
      $.get("/api/v1/catalog", function(data) {
        refreshCatalog(data);
        loadingOff();
      });
    },
    error: function(data) {
      loadingOff();
      return false;
    }
  });
}

function updateItem(id, name, picture, description) {
  if (!id || id == "") {
    console.log('updateItem: Mandatory parameter "id" missing');
    return false;
  }
  if (!name || name == "") {
    console.log('updateItem: Mandatory parameter "name" missing');
    return false;
  }
  if (picture === undefined) {
    picture = "";
  }
  if (description === undefined) {
    description = "";
  }
  loadingOn();
  $.ajax({
    type: "PUT",
    url: "/api/v1/items/" + id,
    contentType: "application/json",
    beforeSend: function(xhr) {
      xhr.setRequestHeader(
        "Authorization",
        "Basic " + btoa(Cookies.get("token") + ":blank")
      );
    },
    data: JSON.stringify({
      name: name,
      picture: picture,
      description: description
    }),
    success: function(data) {
      $.get("/api/v1/catalog", function(data) {
        refreshCatalog(data);
        loadingOff();
      });
    },
    error: function(data) {
      loadingOff();
      return false;
    }
  });
}

function deleteItem(id) {
  if (!id || id == "") {
    console.log('deleteItem: Mandatory parameter "id" missing');
    return false;
  }
  loadingOn();
  $.ajax({
    type: "DELETE",
    url: "/api/v1/items/" + id,
    contentType: "application/json",
    beforeSend: function(xhr) {
      xhr.setRequestHeader(
        "Authorization",
        "Basic " + btoa(Cookies.get("token") + ":blank")
      );
    },
    success: function(data) {
      $.get("/api/v1/catalog", function(data) {
        refreshCatalog(data);
        loadingOff();
      });
    },
    error: function(data) {
      loadingOff();
      return false;
    }
  });
}
