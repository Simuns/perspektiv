var quill = new Quill('#editor', {
  modules: {
      toolbar: [
          ['bold', 'italic', 'underline'],
          [{ 'header': 2 }],
          [{ 'list': 'ordered' }, { 'list': 'bullet' }],
          [{ 'align': [] }],
          ['clean']
      ]
  },
  theme: 'snow'
});
$("#skriva").on("submit",function() {
  var contents = quill.getContents();
  $("#hiddenArea").val($("#editor .ql-editor").html());
})