function test_MakeDocument(){
    makeDocument() 
}
function makeDocument() {
  let ss = SpreadsheetApp.getActiveSpreadsheet()
  let sheet = ss.getSheetByName("Entities")//Change your sheet to this name, or match yours
   let values = sheet.getDataRange().getValues()
let headers = values.shift()//pop the first row off

let data = {}
let words = []
values.forEach( function(row){
  //Value	Type	Confidence	Page	One																					
  let value = row[0] // the first column's data 
  let type = row[1] // the second column's data
  let confidence = row[2]
  let pageNum = row[3]
  if (value in data){
      data[value].count +=1
      data[value].pages.push(pageNum)
  }else{
    data[value] = {count:1, pages:[pageNum]}
    words.push( value )
  }
})

let doc = DocumentApp.create("Index")
let body = doc.getBody()
let countAbove = 3
let previousFirstLetter
words.sort()

for (w in words){
let word = words[w]
let wordObj = data[word]
let firstLetter = word.charAt(0)

if (firstLetter != previousFirstLetter){
  body.appendParagraph(firstLetter).setHeading(DocumentApp.ParagraphHeading.HEADING3)
}

if (wordObj.count > countAbove){
  let pages = wordObj.pages

  var unique_pages = pages.filter(onlyUnique);
  body.appendParagraph( word + " " + unique_pages )
}

previousFirstLetter = firstLetter
}
doc.saveAndClose()
Logger.log( doc.getUrl() )


}

function onlyUnique(value, index, self) {
return self.indexOf(value) === index;
}