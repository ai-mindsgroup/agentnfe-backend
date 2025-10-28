from src.agent.nfe_validator_agent import NFeValidatorAgent
import asyncio

validator = NFeValidatorAgent(llm_provider="google")
result = asyncio.run(validator.validate(csv_path="data/notas_fiscais.csv", has_headers=False))
print(result)
