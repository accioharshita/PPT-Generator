from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool

from pydantic import BaseModel
from typing import List

from src.edu_flow_v2.llm_config import llm


@CrewBase
class Researchers():
	"""Researchers crew"""

	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	@agent
	def topic_explorer(self) -> Agent:
		search_tool = SerperDevTool()
		return Agent(
			config=self.agents_config['topic_explorer'],
			tools=[search_tool],
			llm= llm,
			verbose=True
		)

	@agent
	def indepth_researcher(self) -> Agent:
		search_tool = SerperDevTool()
		return Agent(
			config=self.agents_config['indepth_researcher'],
			tools=[search_tool],
			llm= llm,
			verbose=True,
			memory=True
		)
	
	# @agent
	# def example_finder(self) -> Agent:
	# 	search_tool = EnhancedSerperDevTool()
	# 	return Agent(
	# 		config=self.agents_config['example_finder'],
	# 		tools=[search_tool],
	# 		llm= llm,
	# 		verbose=True,
	# 		memory=True
	# 	)
	
	

	@task
	def topic_exploration_task(self) -> Task:
		return Task(
			config=self.tasks_config['topic_exploration_task'],
			output_file= 'slides.md'
		)

	@task
	def detailed_research_task(self) -> Task:
		return Task(
			config=self.tasks_config['detailed_research_task'],
			output_file='depth.md'
		)
	
	# @task
	# def example_finding_task(self) -> Task:
	# 	return Task(
	# 		config=self.tasks_config['example_finding_task'],
	# 		output_file='example.md'
	# 	)
	
	

	@crew
	def crew(self) -> Crew:
		"""Creates the Researchers crew"""
		# To learn how to add knowledge sources to your crew, check out the documentation:
		# https://docs.crewai.com/concepts/knowledge#what-is-knowledge

		return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=True,
			# process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
		)

