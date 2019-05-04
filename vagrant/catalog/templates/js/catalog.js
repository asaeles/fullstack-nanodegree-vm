// I will be JS template strings to
//  simplify the process of rendering
//  the catalog and its edit buttons

// This variable holds a hide style
//  that will be added by default
//  to all edit buttons on the
//  catalog, its value will depend on
//  the value of the isLoggedIn var
var displayNone = ' style="display: none;"';

// Declarations and variable initialization
//  with dummy values
var catId = 1;
var catName = "Cat 1";
var itemsCount = 14;
var itemId = 2;
var itemName = "Item 2";

// Initialize templates with empty template string
// The templates are split to allow for easy
//  looping
var catHead = ``;
var catRptHead = ``;
var itemHead = ``;
var itemRpt = ``;
var itemFoot = ``;
var catRptFoot = ``;
var catFoot = ``;

// The templates filling will be included
//  into one function to be called with
//  each loop in the catalog
function fillCatalogTemplates() {
  // Fill catalog templates to refresh variables
  catHead = `      <button ${displayNone}
        id="add-category"
        type="button"
        data-toggle="modal"
        data-target="#crud-modal"
        data-crud-title="Add new category"
        data-crud-label="New category name"
        data-crud-placeholder="Category name"
        data-crud-value=""
        data-crud-button="Create"
        data-crud-function="addCategory($('#crud-value').val())"
        class="btn btn-primary mb-3 w-100"
      >
        Add new category
      </button>
      <div id="accordion">
`;
  catRptHead = `        <div class="card">
          <button
            id="heading-${catId}"
            class="card-header list-group-item d-flex justify-content-between align-items-center"
            data-toggle="collapse"
            data-target="#collapse-${catId}"
            aria-expanded="false"
            aria-controls="collapse-${catId}"
          >
            ${catName}
            <div>
              <span ${displayNone}
                class="far fa-edit"
                data-toggle="modal"
                data-target="#crud-modal"
                data-crud-title="Update category '${catName}'"
                data-crud-label="Edit category name"
                data-crud-placeholder="Category name"
                data-crud-value="${catName}"
                data-crud-button="Update"
                data-crud-function="updateCategory(${catId}, $('#crud-value').val())"
                style="min-width: 35px; min-height: 25px;"
              ></span>
              <span ${displayNone}
                class="far fa-trash-alt"
                data-toggle="modal"
                data-target="#crud-modal"
                data-crud-title="Delete category '${catName}'"
                data-crud-label="Delete category '${catName}' and all items below it?"
                data-crud-placeholder="Category name"
                data-crud-value="${catName}"
                data-crud-button="Delete"
                data-crud-function="deleteCategory(${catId})"
                style="min-width: 35px; min-height: 25px;"
              ></span>
              <span class="badge badge-primary badge-pill">${itemsCount}</span>
            </div>
          </button>

          <div
            id="collapse-${catId}"
            class="collapse"
            aria-labelledby="heading-${catId}"
            data-parent="#accordion"
          >
            <div class="card-body">
              <button ${displayNone}
                id="add-item-${catId}"
                type="button"
                data-toggle="modal"
                data-target="#crud-modal"
                data-crud-title="Add new item to '${catName}'"
                data-crud-label="New item name"
                data-crud-placeholder="Item name"
                data-crud-value=""
                data-crud-button="Create"
                data-crud-function="addItem($('#crud-value').val(), ${catId})"
                class="btn btn-primary mb-3 w-100"
              >
                Add new item <span class="d-none d-sm-inline">to '${catName}'</span>
              </button>
`;
  itemHead = `              <ul class="list-group">
`;
  itemRpt = `                <li
                  class="list-group-item d-flex justify-content-between align-items-center"
                >
                  ${itemName}
                  <div ${displayNone}>
                    <span
                      class="far fa-edit"
                      data-toggle="modal"
                      data-target="#crud-modal"
                      data-crud-title="Update item '${itemName}' under category '${catName}'"
                      data-crud-label="Edit item name"
                      data-crud-placeholder="Item name"
                      data-crud-value="${itemName}"
                      data-crud-button="Update"
                      data-crud-function="updateItem(${itemId}, $('#crud-value').val())"
                      style="min-width: 35px; min-height: 25px; cursor: pointer;"
                    ></span>
                    <span
                      class="far fa-trash-alt"
                      data-toggle="modal"
                      data-target="#crud-modal"
                      data-crud-title="Delete item '${itemName}'"
                      data-crud-label="Delete item '${itemName}' under category '${catName}?'"
                      data-crud-placeholder="Item name"
                      data-crud-value="${itemName}"
                      data-crud-button="Delete"
                      data-crud-function="deleteItem(${itemId})"
                      style="min-width: 35px; min-height: 25px; cursor: pointer;"
                    ></span>
                  </div>
                </li>
`;
  itemFoot = `              </ul>
`;
  catRptFoot = `            </div>
          </div>
        </div>
`;
  catFoot = `      </div>
`;
}

// The actual refresh catalog function
function refreshCatalog(catalog) {
  if (isLoggedIn) {
    displayNone = "";
  } else {
    displayNone = ' style="display: none;"';
  }
  fillCatalogTemplates();
  // The variable that will hold the
  //  whole HTML for the catalog
  var catalogHtml = catHead;
  // Two nested loops one for categories
  //  and the other for items
  for (x in catalog) {
    var cat = catalog[x];
    catId = cat.id;
    catName = cat.name;
    itemsCount = cat.items.length;
    fillCatalogTemplates();
    catalogHtml += catRptHead;
    var y = -1;
    for (y in cat.items) {
      var item = cat.items[y];
      itemId = item.id;
      itemName = item.name;
      fillCatalogTemplates();
      // Only add header if there are items
      if (y == 0) {
        catalogHtml += itemHead;
      }
      catalogHtml += itemRpt;
    }
    // Only add footer if there are items
    if (y > -1) {
      catalogHtml += itemFoot;
    }
    catalogHtml += catRptFoot;
  }
  catalogHtml += catFoot;
  $("#container").html(catalogHtml);
}
