for DC in **/*.jpg; 
do 
    if [[ $DC =~ '.*/(HTH [0-9]{4}).*\.jpg' ]]; 
    then 
        curl $DB_URL/death-certs/_find -H "Content-Type: application/json" -d "{\"selector\":{\"Collection ID\":\"$match\"}}" > tmp.json;
        doc=`jq -r '.docs[0]._id' tmp.json`;
        rev=`jq '.docs[0]._rev' tmp.json`;
        file=$DC:t
        file=${file// /-}
        echo $DC $doc $rev
        curl -X PUT $DB_URL/death-certs/$doc/$file -H "If-Match: $rev" -H "Content-Type: image/jpeg" --data-binary @$DC
    fi; 
done
