from autonomous_job_agent.tools.brain import Brain
b = Brain()
# Mock resumes if folder empty, else relies on existing data
if not b.full_resumes: b.full_resumes = {"test_resume": "skills: python, ai, robotics"}
strategies = b.generate_initial_strategy()
print(strategies)