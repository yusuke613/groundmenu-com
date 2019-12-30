//ログイン時のフォームに関するjs
$(function(){
  $(".js-registration").click(function(){
    $.when($(".js-form--login").slideUp()
      ).done(function() {
    $(".js-form--registration").slideDown();
    });
  });
});

$(function(){
  $(".js-login").click(function(){
    $.when($(".js-form--registration").slideUp()
      ).done(function() {
    $(".js-form--login").slideDown();
    });
  });
});


//サイドメニュー表示に関するjs
$(document).on('click', '.js-header__menu', function(){
//レスポンシブ対応のための閾値
  var device_width = $(window).width();
// サイドメニューを隠す処理は同じ
    if($(this).hasClass("js-header__menu--doing")){
      $(this).removeClass("js-header__menu--doing");
      $("body").removeClass("overflow-hidden"); //サイドメニューが表示されることで起こるレイアウトの崩れのhiddenを解除
      $(".wrapper__side").animate({width:"0vw"}, 250);
      $(".wrapper__main").animate({width:"100vw"},250);
      $(".wrapper__main").animate({left:"0vw"}, 250);
    }else{
// サイドメニューを表示する処理
      $(this).addClass("js-header__menu--doing");
      $("body").addClass("overflow-hidden"); //サイドメニューが表示されることで起こるレイアウトの崩れをhiddenで回避
// ディスプレイサイズによって、どこまで表示するかを選択する
    if(device_width < 768){
      $(".wrapper__side").animate({width:"100vw"}, 250);
      $(".wrapper__main").animate({width:"0vw"},250);
      $(".wrapper__main").animate({left:"100vw"}, 250);
    }else if(device_width < 1024){
      $(".wrapper__side").animate({width:"50vw"}, 250);
      $(".wrapper__main").animate({width:"50vw"},250);
      $(".wrapper__main").animate({left:"50vw"}, 250);
    }else{
      $(".wrapper__side").animate({width:"25vw"}, 250);
      $(".wrapper__main").animate({width:"75vw"},250);
      $(".wrapper__main").animate({left:"25vw"}, 250);
    };
  };
});
//グローバルナビの小メニュー表示に関するjs
$(document).on('click', '.js-side_menu_1__opener', function(){
  if($(this).hasClass("js-icon_pulus--doing")){
    $(this).removeClass("js-icon_pulus--doing");
    $(this).parent("li").css("background-color","#FFA500");
    $(this).parent("li").next(".side_menu_2").slideUp();
  }else{
    $(this).addClass("js-icon_pulus--doing");
    $(this).parent("li").next(".side_menu_2").slideDown();
    $(this).parent("li").css("background-color","#072A24");
  };
});


// メニュー追加のためのLightboxを表示
$(function() {
  $(".button__add").click(function(){
    $.when($(".lightbox--add").css("display", "flex")).done(function(){
     $(".lightbox--add").animate({left:"0%"}, 250);
    });
  });
});

// メニュー追加のためのLightboxを消す
$(function() {
  $(".lightbox--add__back").click(function(){
    $.when($(".lightbox--add").animate({left:"100%"}, 250)).done(function(){
      $(".lightbox--add").css("display", "none");
    });
  });
});

// 中分類類メニュー表示
$(function(){
  $(".js-food").click(function(){
    $.when($(".js-sortable_class_2--drink").slideUp()
      ).done(function() {
    $(".js-sortable_class_2--food").slideDown();
    });
  });
});

$(function(){
  $(".js-drink").click(function(){
    $.when($(".js-sortable_class_2--food").slideUp()
      ).done(function() {
    $(".js-sortable_class_2--drink").slideDown();
    });
  });
});

// 小分類メニューを表示する
$(function() {
  $(".menu_box--class_2").click(function(){
    var selector = $(this).attr('value')
    $("." + selector).css("display", "flex");
    $(".lightbox--class_3__back").css("display", "inline-block");
    $.when($(".lightbox--class_3").css("display", "flex")).done(function(){
      $(".lightbox--class_3").animate({left:"0%"}, 250);
    });
  });
});

// 小分類のメニューを消す
$(function() {
  $(".lightbox--class_3__back").click(function(){
    $(".lightbox--class_3 li").css("display", "none");
    $(".lightbox--class_3__back").css("display", "none");
    $.when($(".lightbox--class_3").animate({left:"100%"}, 250)).done(function(){
      $(".lightbox--class_3").css("display", "none");
    });
  });
});

// ドラック&ドロップでメニューの順番を並べ替える関数
$(document).on('click', '.button__sortable', function() {
  $(this).remove();
  $('<button form="sort_menu" id="sort_submit" class="button__sortable--active" type="button">⇅</button>').insertBefore(".button__add");
  $(".menu_box--class_2").addClass("vibration");
  $(".menu_box--class_3").addClass("vibration");
  $(".menu_box--class_2").css(
    "background-color","#BF7C00"
    );
  $(".menu_box--class_3").css(
    "background-color","#BF7C00"
    );
// ソートの順番を保存する処理
  $(".js-sortable_class_2--food").sortable();
  $(".js-sortable_class_2--drink").sortable();
  $(".js-sortable_class_3").sortable();
});

$(document).on("click", "#sort_submit", function () {
  var class_2_sort_result_food = $(".js-sortable_class_2--food").sortable("toArray", { attribute: 'id'});
  $("#class_2_sort_result_food").val(class_2_sort_result_food);
  var class_2_sort_result_drink = $(".js-sortable_class_2--drink").sortable("toArray", { attribute: 'id'});
  $("#class_2_sort_result_drink").val(class_2_sort_result_drink);
  var class_3_sort_result = $(".js-sortable_class_3").sortable("toArray", { attribute: 'id'});
  $("#class_3_sort_result").val(class_3_sort_result);
  $("#sort_menu").submit();
});

// デリートボタンを押した後の挙動
$(function(){
  $(".button__delete").click(function(){
// 一度ボタンを消した後に、同じ場所にsubmit属性を持ったボタンを追加する
  $(this).remove();
  $('<button form="delete_menu" class="button__delete--active" type="submit">ー</button>').insertAfter(".button__add");
// vibrationクラスを追加して震えさせる
  $(".menu_box--class_2").addClass("vibration");
  $(".menu_box--class_3").addClass("vibration");
// 色を変える
  $(".menu_box--class_2").css("background-color","#DC3B00");
  $(".menu_box--class_3").css("background-color","#DC3B00");
// deleteというチェックボックスを使えるようにする
  $(".delete").prop("disabled", false);
  });
});

// デリートのチェックが入ったときの処理
$(document).on("click", ".menu_box--class_3", function () {
// 子要素のチェックボックスが入力可能かどうか判定し、無理なら何もしない
  if($(this).children("input:checkbox").prop("disabled") == false){
// 子要素のチェックボックスにチェックが入っているか判定し、チェックが入っていればチェックを取る。入ってなければ入れる
    if($(this).children("input:checkbox").prop("checked") == true){
      $(this).children("input:checkbox").prop('checked', false);
      $(this).css("background-color","#DC3B00");
    }else{
      $(this).children("input:checkbox").prop('checked', true);
      $(this).css("background-color","#401100");
    };
  }else{
  };
});

// 注文数量の隣の+を押した後の処理
$(document).on("click", ".menu_box--class_3__increase", function () {
  var order_quantity_befor = $(this).siblings('input[type="number"]').val();
  if(order_quantity_befor == ""){
    $(this).siblings('input[type="number"]').val(1)
  }else{
    // parseIntで数字として足し算
    order_quantity = parseInt(order_quantity_befor) + parseInt(1);
    $(this).siblings('input[type="number"]').val(order_quantity)
  };
});

// 注文数量の隣の-を押した後の処理
$(document).on("click", ".menu_box--class_3__decrease", function () {
  var order_quantity_befor = $(this).siblings('input[type="number"]').val();
  if(order_quantity_befor == "" || order_quantity_befor == 1 || order_quantity_befor == 0){
    $(this).siblings('input[type="number"]').val("")
  }else{
    // parseIntで数字として足し算
    order_quantity = parseInt(order_quantity_befor) - parseInt(1);
    $(this).siblings('input[type="number"]').val(order_quantity)
  };
});

// オーダーを追加したときにカートに加える仕組み
// $(document).on("click", ".menu_box--class_3__add_to_cart", function () {
//   var quantity = $(this).siblings(".text_box--quantity").val()
//   //正の数且つ整数の時のみカートに加える判定
//   if(quantity > 0 && Number.isInteger(quantity) == false){
//     // add_orderの変数に加える情報は menu_id, class_3, price, quantity
//     var add_order = $(this).siblings('input[type="checkbox"]').attr("value") +
//       "," + $(this).siblings(".text_box--quantity").val()
//     ;
//     console.log(add_order);
//     var add_order_json = {
//     "add_order": add_order
//     }
//     $.ajax({
//       url: "/add_to_cart_json",
//       type: 'post',
//       data: JSON.stringify(add_order_json),
//       dataType: 'json',
//       contentType: 'application/json',
//     })
//     .done(function(data, textStatus, jqXHR){
//       $(".header__quantity").remove();
//       $('<div class="header__quantity"></div>').appendTo(".header__cart");
//       console.log(data);
//       $('.header__quantity').text(data);
//     })
//     .fail(function(data, textStatus, jqXHR){
//     });
//   }else{};
// });

// カート内を確認する
$(document).on("click", ".header__cart", function () {
  if($(".lightbox--order").css("display") == "none"){
    $.when($(".lightbox--order").css("display", "block")).done(function(){
      $(".lightbox--order").animate({left:"0%"}, 250)
    });
  }else{
    $.when($(".lightbox--order").animate({left:"100%"}, 250)).done(function(){
      $(".lightbox--order").css("display", "none");
    });
  };
});

// オーダーリスト表示中に+を押した後の処理
// $(document).on("click", ".menu_box--order__increase", function () {
//   var order_quantity_befor = $(this).next(".text_box--quantity").val();
//   var order_quantity_after = parseInt(order_quantity_befor) + parseInt(1);
//   var change_order = $(this).parent().attr("id").replace("order_id_", "") + "," + order_quantity_after;
//     console.log(change_order);
//     var change_order_json = {"change_order":change_order}
//   $.ajax({
//     url: "/change_cart_json",
//     type: 'post',
//     data: JSON.stringify(change_order_json),
//     dataType: 'json',
//     contentType: 'application/json',
//   })
//   .done(function(data, textStatus, jqXHR){
//     order_id = "order_id_" + data
//     $("#" + order_id).children(".text_box--quantity").val(order_quantity_after);
//     var new_subtotal = parseInt($("#" + order_id).children('.menu_box--order__price').text().replace("¥ ", "")) * parseInt($("#" + order_id).children('.text_box--quantity').val());
//     $("#" + order_id).children('.menu_box--order__subtotal').text("小計 ¥ " + new_subtotal);
//     total_quantity = parseInt($('.header__quantity').text());
//     $('.header__quantity').text(total_quantity+1)
//   })
//   .fail(function(data, textStatus, jqXHR){
//   });
// });

// // オーダーリスト表示中に-を押した後の処理
// $(document).on("click", ".menu_box--order__decrease", function () {
//   var order_quantity_befor = $(this).prev(".text_box--quantity").val();
//   var order_quantity_after = parseInt(order_quantity_befor) - parseInt(1);
//   var change_order = $(this).parent().attr("id").replace("order_id_", "") + "," + order_quantity_after;
//   console.log(change_order);
//   var change_order_json = {"change_order":change_order}
//   $.ajax({
//     url: "/change_cart_json",
//     type: 'post',
//     data: JSON.stringify(change_order_json),
//     dataType: 'json',
//     contentType: 'application/json',
//   })
//   .done(function(data, textStatus, jqXHR){
//     order_id = "order_id_" + data
//     if(order_quantity_after == 0){
//       $("#" + order_id).remove()
//     }else{
//       $("#" + order_id).children(".text_box--quantity").val(order_quantity_after);
//       var new_subtotal = parseInt($("#" + order_id).children('.menu_box--order__price').text().replace("¥ ", "")) * parseInt($("#" + order_id).children('.text_box--quantity').val());
//       $("#" + order_id).children('.menu_box--order__subtotal').text("小計 ¥ " + new_subtotal);
//     }
//     total_quantity = parseInt($('.header__quantity').text());
//     $('.header__quantity').text(total_quantity-1)
//   })
//   .fail(function(data, textStatus, jqXHR){
//   });
// });

// オーダーリストの時ゴミ箱を押した後の処理
// $(document).on("click", ".menu_box--order__garbage", function () {
//   var order_quantity_befor = parseInt($(this).siblings(".text_box--quantity").val());
//   var change_order = $(this).parent().attr("id").replace("order_id_", "") + ",0";
//   var change_order_json = {"change_order":change_order}
//   $.ajax({
//     url: "/change_cart_json",
//     type: 'post',
//     data: JSON.stringify(change_order_json),
//     dataType: 'json',
//     contentType: 'application/json',
//   })
//   .done(function(data, textStatus, jqXHR){
//     order_id = "order_id_" + data
//     $("#" + order_id).remove()
//     total_quantity = parseInt($('.header__quantity').text());
//     $('.header__quantity').text(total_quantity - order_quantity_befor)
//   })
//   .fail(function(data, textStatus, jqXHR){
//   });
// });

// オーダーリストの確認から戻る処理
$(document).on("click", ".lightbox--order__back", function () {
  $.when($(this).parent().animate({left:"100%"}, 250)).done(function(){
    $(".lightbox--order").css("display", "none");
  });
});

// テーブルアクティベートの処理
$(document).on("click", ".table_activate__checkbox", function () {

  var table_number = $(this).attr("id").replace("table_", "");
  if($(this).prop("checked") == true) {
    var activate_status = 1
  }else{
    var activate_status = 0
  };
  var data = {
  "table_number": table_number,
  "activate_status": activate_status
  }
  console.log(data);
  $.ajax({
    url: "/activate_json",
    type: 'post',
    data: JSON.stringify(data),
    dataType: 'json',
    contentType: 'application/json',
  })
  .done(function(data, textStatus, jqXHR){
    console.log(data)
  });

});

// テーブルアクティベートのテーブル状況と、オーダー状況に関する記述
$(function(){
  $(".js-order").click(function(){
    $.when(
    $(".table_activate__wrap").slideUp()
      ).done(function() {
    $(".order_list__wrap").slideDown().css("display", "flex");
    });
  });
});

$(function(){
  $(".js-activate").click(function(){
    $.when(
    $(".order_list__wrap").slideUp()
      ).done(function() {
    $(".table_activate__wrap").slideDown();
    });
  });
});






