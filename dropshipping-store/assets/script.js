document.addEventListener("DOMContentLoaded", function () {
  // Gallery
  var mainImg = document.querySelector(".gallery-main img");
  var thumbs = document.querySelectorAll(".gallery-thumbs img");
  thumbs.forEach(function (thumb) {
    thumb.addEventListener("click", function () {
      mainImg.src = thumb.src.replace("_220x220q75", "_960x960q75");
      thumbs.forEach(function (t) { t.classList.remove("active"); });
      thumb.classList.add("active");
    });
  });

  // Size selector
  var sizeButtons = document.querySelectorAll(".size-grid button");
  sizeButtons.forEach(function (btn) {
    btn.addEventListener("click", function () {
      sizeButtons.forEach(function (b) { b.classList.remove("selected"); });
      btn.classList.add("selected");
    });
  });

  // Size guide toggle
  var guideLink = document.querySelector(".size-guide-link");
  var guideTable = document.querySelector(".size-guide-table");
  if (guideLink && guideTable) {
    guideLink.addEventListener("click", function () {
      guideTable.style.display = guideTable.style.display === "block" ? "none" : "block";
    });
  }

  // FAQ accordion
  document.querySelectorAll(".faq-item").forEach(function (item) {
    var q = item.querySelector(".faq-q");
    q.addEventListener("click", function () {
      var wasOpen = item.classList.contains("open");
      document.querySelectorAll(".faq-item").forEach(function (i) { i.classList.remove("open"); });
      if (!wasOpen) item.classList.add("open");
    });
  });
});
