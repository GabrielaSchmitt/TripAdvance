// configurações scheduled - advanced: 00 00 * * *
// function:

const LIMITE_BYTES = 10000; // Defina o limite desejado, ex.: 10 * 1024 * 1024 para 10MB

exports = async function() {
    console.log("Trigger iniciado.");

    function isProcessingAllowed() {
        const now = new Date();
        const currentHour = now.getHours();
        const currentMinute = now.getMinutes();
        return (currentHour >= 0 && currentHour < 5) || 
               (currentHour === 5 && currentMinute <= 30);
    }

    if (!isProcessingAllowed()) {
        return { 
            message: "Fora do horário de processamento",
            nextCheck: "Reagendado para próxima janela"
        };
    } 

    let uploadedFilesCollection;
    try {
        // Referência ao serviço do MongoDB Atlas
        const mongodb = context.services.get("TripAdvanceDB");
        if (!mongodb) {
            throw new Error("Serviço MongoDB Atlas não encontrado no contexto.");
        }

        // Acessa a base de dados e a coleção
        const db = mongodb.db("tripadv_qas");
        uploadedFilesCollection = db.collection("uploaded_files");
    } catch (error) {
        console.error("Erro ao acessar o MongoDB Atlas:", error.message);
        return {
            error: "Falha ao acessar o MongoDB Atlas.",
            details: error.message,
        };
    }

    try {
        console.log("Buscando arquivos pendentes para processamento...");

        const arquivosPendentes = await uploadedFilesCollection
            .find({ 
                trained: false,
                datetime: { $lt: new Date(Date.now() - 60 * 60 * 1000) } 
            })
            .sort({ datetime: 1 }) // Ordena do mais antigo para o mais novo
            .toArray();

        console.log(`Arquivos pendentes encontrados: ${arquivosPendentes.length}`);

        let totalBytes = 0;
        const arquivosParaProcessar = [];

        // Seleciona arquivos até atingir o limite
        for (const arquivo of arquivosPendentes) {
            if (totalBytes + arquivo.size <= LIMITE_BYTES) {
                totalBytes += arquivo.size;
                arquivosParaProcessar.push(arquivo);
            } else {
                break;
            }

            totalBytes += arquivo.size; // Adiciona todos os arquivos sem verificar o limite
            arquivosParaProcessar.push(arquivo); // Adiciona os arquivos à lista para processamento
        }

        // Verifica se há arquivos para processar
        if (arquivosParaProcessar.length > 0) {
            const payload = {
                arquivos: arquivosParaProcessar.map(file => ({ 
                    id: file._id, 
                    nome: file.file,
                    size: file.size,
                    data: file.data
                })),
                totalSize: totalBytes
            };


            // Exibe o payload no console para verificação
            console.log("Payload enviado para AWS Step Functions:", JSON.stringify(payload, null, 2));

            console.log("Enviando payload para AWS Step Functions...");

            const stepFunctionsResponse = await context.http.post({
                url: "https://states.sa-east-1.amazonaws.com",
                body: JSON.stringify({
                    stateMachineArn: "arn:aws:states:sa-east-1:794038239675:stateMachine:TripAdvance",
                    input: JSON.stringify(payload)
                }),
                headers: {
                    "Content-Type": ["application/json"],
                    "X-Amz-Target": ["AWSStepFunctions.StartExecution"]
                }
            });

            console.log("Resposta AWS Step Functions:", stepFunctionsResponse);
            
            
            // Verifica se a resposta da AWS foi bem-sucedida
            if (stepFunctionsResponse.status === 200 && stepFunctionsResponse.body) {
                const responseBody = JSON.parse(stepFunctionsResponse.body);
                
                // Caso a resposta da AWS indique sucesso, atualiza o status no banco
                if (responseBody.status === 'SUCESSO') { // Verifique o valor correto do status de sucesso
                    console.log("Atualizando status dos arquivos selecionados...");

                    await uploadedFilesCollection.updateMany(
                        { _id: { $in: arquivosParaProcessar.map(a => a._id) } },
                        { $set: { 
                            trained: true, 
                            trainedAt: new Date() 
                        } }
                    );

                    console.log("Status atualizado com sucesso.");
                } else {
                    console.log("Erro na execução do Step Functions:", responseBody.message || 'Sem mensagem de erro.');
                    return { 
                        message: "Erro no processamento da AWS Step Functions", 
                        details: responseBody.message 
                    };
                }
            } else {
                console.log("Erro na resposta da AWS Step Functions ou falha de comunicação.");
                return { 
                    message: "Erro na resposta da AWS Step Functions", 
                    details: stepFunctionsResponse.body 
                };
            }
        } else {
            return { 
                message: "Nenhum arquivo pendente para processamento" 
            };
        }

        return { 
            message: "Tamanho mínimo não atingido",
            currentTotalSize: totalBytes,
            minimumThreshold: LIMITE_BYTES
        };
    } catch (error) {
        console.error("Erro durante o processamento:", error.message);
        return {
            error: error.message,
            stack: error.stack
        };
    }
};